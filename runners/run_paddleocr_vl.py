"""
PaddleOCR-VL benchmark runner (Modal GPU).
Uses PaddlePaddle's PP-OCRv4 for OCR.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared import get_test_images, save_results, get_logger

log = get_logger("paddleocr_vl")

try:
    import modal

    # Find shared.py relative to this script
    shared_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "shared.py")
    
    app = modal.App("ocr-benchmark-paddle")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .apt_install("libgl1", "libglib2.0-0", "libgomp1")
        .pip_install("paddlepaddle", "paddleocr==2.8.1")
        .add_local_file(shared_path, remote_path="/root/shared.py")
    )

    @app.function(image=image, timeout=1200)
    def run_paddleocr_modal(image_bytes_list: list) -> list:
        from paddleocr import PaddleOCR
        from PIL import Image
        import io
        import numpy as np

        ocr_en = PaddleOCR(use_angle_cls=True, lang="en")

        results = []
        for item in image_bytes_list:
            img = np.array(Image.open(io.BytesIO(item["bytes"])).convert("RGB"))
            start = time.time()
            try:
                result = ocr_en.ocr(img, cls=True)
                texts = []
                bboxes = []
                if result and result[0]:
                    for line in result[0]:
                        # line is typically [ [[x1,y1],...], ("text", confidence) ]
                        if line[0]:
                            # Convert boxes to int to be JSON serialisable
                            bboxes.append([[int(p[0]), int(p[1])] for p in line[0]])
                        if line[1]:
                            texts.append(line[1][0])
                elapsed = time.time() - start
                results.append({
                    "name": item["name"],
                    "category": item.get("category", "unknown"),
                    "ocr_text": "\n".join(texts),
                    "bounding_boxes": bboxes,
                    "latency_s": round(elapsed, 3),
                    "status": "success",
                })
            except Exception as e:
                elapsed = time.time() - start
                results.append({
                    "name": item["name"],
                    "category": item.get("category", "unknown"),
                    "ocr_text": "",
                    "bounding_boxes": None,
                    "latency_s": round(elapsed, 3),
                    "status": f"error: {str(e)}",
                })
        return results

    HAS_MODAL = True
except ImportError:
    HAS_MODAL = False


def run_local_fallback():
    log.warning("PaddleOCR requires Modal GPU — generating placeholders")
    docs = get_test_images(as_bytes=True)
    placeholders = [
        {"name": d["name"], "category": d.get("category", "unknown"),
         "ocr_text": "[placeholder]", "latency_s": 0.0, "status": "placeholder"}
        for d in docs
    ]
    save_results("paddleocr_vl", placeholders, extra_meta={"note": "LOCAL FALLBACK"})


def main():
    if HAS_MODAL:
        log.info("Running PaddleOCR on Modal GPU...")
        docs = get_test_images(as_bytes=True)
        with modal.enable_output():
            with app.run():
                modal_results = run_paddleocr_modal.remote(docs)
        save_results("paddleocr_vl", modal_results)
    else:
        run_local_fallback()


if __name__ == "__main__":
    main()
