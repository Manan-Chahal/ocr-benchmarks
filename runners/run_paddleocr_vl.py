"""
PaddleOCR-VL benchmark runner (Modal GPU).
Uses PaddlePaddle's PP-OCRv4 for OCR.
"""

import json
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

try:
    import modal

    app = modal.App("ocr-benchmark-paddleocr")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .apt_install("libgl1-mesa-glx", "libglib2.0-0")
        .pip_install("paddlepaddle-gpu", "paddleocr", "Pillow")
    )

    @app.function(image=image, gpu="T4", timeout=1200)
    def run_paddleocr_modal(image_bytes_list: list) -> list:
        from paddleocr import PaddleOCR
        from PIL import Image
        import io
        import numpy as np

        ocr_en = PaddleOCR(use_angle_cls=True, lang="en", use_gpu=True)

        results = []
        for item in image_bytes_list:
            img = np.array(Image.open(io.BytesIO(item["bytes"])).convert("RGB"))
            start = time.time()
            try:
                result = ocr_en.ocr(img, cls=True)
                texts = []
                if result and result[0]:
                    for line in result[0]:
                        if line[1]:
                            texts.append(line[1][0])
                elapsed = time.time() - start
                results.append({
                    "name": item["name"],
                    "ocr_text": "\n".join(texts),
                    "latency_s": round(elapsed, 3),
                    "status": "success",
                })
            except Exception as e:
                elapsed = time.time() - start
                results.append({
                    "name": item["name"],
                    "ocr_text": "",
                    "latency_s": round(elapsed, 3),
                    "status": f"error: {str(e)}",
                })
        return results

    HAS_MODAL = True
except ImportError:
    HAS_MODAL = False


def get_test_images():
    docs = []
    for subdir in ["scanned", "handwritten"]:
        folder = os.path.join(BASE, "test_documents", subdir)
        if os.path.exists(folder):
            for f in sorted(os.listdir(folder)):
                if f.lower().endswith((".png", ".jpg", ".jpeg")):
                    with open(os.path.join(folder, f), "rb") as fh:
                        docs.append({"name": f, "bytes": fh.read(), "category": subdir})

    printed_dir = os.path.join(BASE, "test_documents", "printed")
    if os.path.exists(printed_dir):
        try:
            import fitz
            for f in sorted(os.listdir(printed_dir)):
                if f.lower().endswith(".pdf"):
                    doc = fitz.open(os.path.join(printed_dir, f))
                    for pg in range(len(doc)):
                        pix = doc[pg].get_pixmap(dpi=200)
                        docs.append({"name": os.path.splitext(f)[0], "bytes": pix.tobytes("png"), "category": "printed"})
                    doc.close()
        except ImportError:
            pass
    return docs


def run_local_fallback():
    print("WARNING: PaddleOCR requires Modal GPU. Generating placeholders.")
    docs = get_test_images()
    results = {"model": "paddleocr_vl", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
               "note": "LOCAL FALLBACK", "documents": []}
    for d in docs:
        results["documents"].append({"name": d["name"], "category": d["category"],
                                     "ocr_text": "[placeholder]", "latency_s": 0.0, "status": "placeholder"})
    out = os.path.join(RESULTS_DIR, "paddleocr_vl_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Saved to {out}")


def main():
    if HAS_MODAL:
        print("Running PaddleOCR on Modal GPU...")
        docs = get_test_images()
        with modal.enable_output():
            with app.run():
                modal_results = run_paddleocr_modal.remote(docs)
        results = {"model": "paddleocr_vl", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "documents": modal_results}
        out = os.path.join(RESULTS_DIR, "paddleocr_vl_results.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {out}")
    else:
        run_local_fallback()


if __name__ == "__main__":
    main()
