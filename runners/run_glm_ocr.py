"""
GLM-OCR benchmark runner (Modal GPU).
Uses the GLM-4V-9B model via transformers for OCR.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared import get_test_images, save_results, get_logger

log = get_logger("glm_ocr")

# ── Modal-based runner ───────────────────────────────────────────────────────
try:
    import modal

    # Find shared.py relative to this script
    shared_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "shared.py")
    
    app = modal.App("ocr-benchmark-glm")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install(
            "torch", "torchvision", "transformers==4.40.1", "accelerate",
            "Pillow", "sentencepiece", "protobuf", "tiktoken",
        )
        .add_local_file(shared_path, remote_path="/root/shared.py")
    )

    @app.function(image=image, gpu="A10G", timeout=1800, memory=32768)
    def run_glm_ocr_modal(image_bytes_list: list) -> list:
        """Run GLM-OCR on a list of images on Modal GPU."""
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from PIL import Image
        import io
        import torch

        model_id = "THUDM/glm-4v-9b"
        print(f"Loading model {model_id}...")

        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype=torch.float16,
            device_map="auto", trust_remote_code=True,
        )

        results = []
        for item in image_bytes_list:
            name = item["name"]
            img = Image.open(io.BytesIO(item["bytes"])).convert("RGB")
            prompt = "Please extract all text from this image. Return only the extracted text."
            start = time.time()
            try:
                inputs = tokenizer.apply_chat_template(
                    [{"role": "user", "image": img, "content": prompt}],
                    add_generation_prompt=True, tokenize=True,
                    return_tensors="pt", return_dict=True,
                ).to(model.device)
                output = model.generate(**inputs, max_new_tokens=2048)
                text = tokenizer.decode(
                    output[0][inputs["input_ids"].shape[1]:],
                    skip_special_tokens=True,
                )
                elapsed = time.time() - start
                results.append({
                    "name": name,
                    "category": item.get("category", "unknown"),
                    "ocr_text": text.strip(),
                    "bounding_boxes": None,
                    "latency_s": round(elapsed, 3),
                    "status": "success",
                })
            except Exception as e:
                elapsed = time.time() - start
                results.append({
                    "name": name,
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
    """Generate placeholder results when Modal is unavailable."""
    log.warning("GLM-OCR requires Modal GPU — generating placeholder results")
    docs = get_test_images(as_bytes=True)
    placeholders = [
        {"name": d["name"], "category": d.get("category", "unknown"),
         "ocr_text": "[placeholder]", "latency_s": 0.0, "status": "placeholder"}
        for d in docs
    ]
    save_results("glm_ocr", placeholders, extra_meta={"note": "LOCAL FALLBACK"})


def main():
    if HAS_MODAL:
        log.info("Running GLM-OCR on Modal GPU...")
        docs = get_test_images(as_bytes=True)
        log.info("Prepared %d documents", len(docs))
        with modal.enable_output():
            with app.run():
                modal_results = run_glm_ocr_modal.remote(docs)
        save_results("glm_ocr", modal_results)
    else:
        run_local_fallback()


if __name__ == "__main__":
    main()
