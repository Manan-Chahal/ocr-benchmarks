"""
olmOCR-2 benchmark runner (Modal GPU).
Uses allenai/olmOCR-7B-0225-preview for OCR via transformers.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared import get_test_images, save_results, get_logger

log = get_logger("olmocr2")

try:
    import modal

    # Find shared.py relative to this script
    shared_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "shared.py")
    
    app = modal.App("ocr-benchmark-olmocr2")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install(
            "torch", "torchvision", "transformers>=4.45", "accelerate",
            "Pillow"
        )
        .add_local_file(shared_path, remote_path="/root/shared.py")
    )

    @app.function(image=image, gpu="A10G", timeout=1800, memory=32768)
    def run_olmocr_modal(image_bytes_list: list) -> list:
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        from PIL import Image
        import io
        import torch

        model_id = "allenai/olmOCR-7B-0225-preview"
        print(f"Loading {model_id}...")

        processor = AutoProcessor.from_pretrained(model_id)
        model = Qwen2VLForConditionalGeneration.from_pretrained(
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
                results.append({
                    "name": item["name"],
                    "category": item.get("category", "unknown"),
                    "ocr_text": text.strip(),
                    "bounding_boxes": None,
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
    log.warning("olmOCR-2 requires Modal GPU — generating placeholders")
    docs = get_test_images(as_bytes=True)
    placeholders = [
        {"name": d["name"], "category": d.get("category", "unknown"),
         "ocr_text": "[placeholder]", "latency_s": 0.0, "status": "placeholder"}
        for d in docs
    ]
    save_results("olmocr2", placeholders, extra_meta={"note": "LOCAL FALLBACK"})


def main():
    if HAS_MODAL:
        log.info("Running olmOCR-2 on Modal GPU...")
        docs = get_test_images(as_bytes=True)
        with modal.enable_output():
            with app.run():
                modal_results = run_olmocr_modal.remote(docs)
        save_results("olmocr2", modal_results)
    else:
        run_local_fallback()


if __name__ == "__main__":
    main()
