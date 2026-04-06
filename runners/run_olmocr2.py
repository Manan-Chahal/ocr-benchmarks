"""
olmOCR-2 benchmark runner (Modal GPU).
Uses allenai/olmOCR-2 for OCR via transformers.
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

    app = modal.App("ocr-benchmark-olmocr2")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install(
            "torch", "torchvision", "transformers>=4.40", "accelerate",
            "Pillow", "sentencepiece",
        )
    )

    @app.function(image=image, gpu="A10G", timeout=1800, memory=32768)
    def run_olmocr_modal(image_bytes_list: list) -> list:
        from transformers import AutoModelForVision2Seq, AutoProcessor
        from PIL import Image
        import io
        import torch

        model_id = "allenai/olmOCR-7B-0225-preview"
        print(f"Loading {model_id}...")

        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForVision2Seq.from_pretrained(
            model_id, torch_dtype=torch.float16, device_map="auto"
        )

        results = []
        for item in image_bytes_list:
            img = Image.open(io.BytesIO(item["bytes"])).convert("RGB")
            start = time.time()
            try:
                prompt = "Extract all the text content from this document image."
                messages = [{"role": "user", "content": [
                    {"type": "image", "image": img},
                    {"type": "text", "text": prompt},
                ]}]

                text_prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = processor(
                    text=text_prompt, images=[img], return_tensors="pt"
                ).to(model.device)

                output_ids = model.generate(**inputs, max_new_tokens=2048)
                text = processor.batch_decode(
                    output_ids[:, inputs["input_ids"].shape[1]:],
                    skip_special_tokens=True
                )[0]
                elapsed = time.time() - start

                results.append({"name": item["name"], "ocr_text": text.strip(),
                                "latency_s": round(elapsed, 3), "status": "success"})
            except Exception as e:
                elapsed = time.time() - start
                results.append({"name": item["name"], "ocr_text": "",
                                "latency_s": round(elapsed, 3), "status": f"error: {str(e)}"})
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
    print("WARNING: olmOCR-2 requires Modal GPU. Generating placeholders.")
    docs = get_test_images()
    results = {"model": "olmocr2", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
               "note": "LOCAL FALLBACK", "documents": []}
    for d in docs:
        results["documents"].append({"name": d["name"], "category": d["category"],
                                     "ocr_text": "[placeholder]", "latency_s": 0.0, "status": "placeholder"})
    out = os.path.join(RESULTS_DIR, "olmocr2_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Saved to {out}")


def main():
    if HAS_MODAL:
        print("Running olmOCR-2 on Modal GPU...")
        docs = get_test_images()
        with modal.enable_output():
            with app.run():
                modal_results = run_olmocr_modal.remote(docs)
        results = {"model": "olmocr2", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "documents": modal_results}
        out = os.path.join(RESULTS_DIR, "olmocr2_results.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {out}")
    else:
        run_local_fallback()


if __name__ == "__main__":
    main()
