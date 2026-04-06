"""
GLM-OCR benchmark runner (Modal GPU).
Uses the GLM-4V-9B model via transformers for OCR.
"""

import json
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Modal-based runner
try:
    import modal

    app = modal.App("ocr-benchmark-glm")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install(
            "torch", "torchvision", "transformers==4.40.1", "accelerate",
            "Pillow", "sentencepiece", "protobuf", "tiktoken",
        )
    )

    @app.function(
        image=image,
        gpu="A10G",
        timeout=1800,
        memory=32768,
    )
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
            model_id,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
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
                    add_generation_prompt=True,
                    tokenize=True,
                    return_tensors="pt",
                    return_dict=True,
                ).to(model.device)

                output = model.generate(**inputs, max_new_tokens=2048)
                text = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
                elapsed = time.time() - start

                results.append({
                    "name": name,
                    "ocr_text": text.strip(),
                    "latency_s": round(elapsed, 3),
                    "status": "success",
                })
            except Exception as e:
                elapsed = time.time() - start
                results.append({
                    "name": name,
                    "ocr_text": "",
                    "latency_s": round(elapsed, 3),
                    "status": f"error: {str(e)}",
                })

        return results

    HAS_MODAL = True
except ImportError:
    HAS_MODAL = False


def get_test_images():
    """Collect test images as bytes for Modal transfer."""
    from PIL import Image
    import io

    docs = []

    for subdir in ["scanned", "handwritten"]:
        folder = os.path.join(BASE, "test_documents", subdir)
        if os.path.exists(folder):
            for f in sorted(os.listdir(folder)):
                if f.lower().endswith((".png", ".jpg", ".jpeg")):
                    with open(os.path.join(folder, f), "rb") as fh:
                        docs.append({"name": f, "bytes": fh.read(), "category": subdir})

    # Convert PDFs to images
    printed_dir = os.path.join(BASE, "test_documents", "printed")
    if os.path.exists(printed_dir):
        try:
            import fitz
            for f in sorted(os.listdir(printed_dir)):
                if f.lower().endswith(".pdf"):
                    doc = fitz.open(os.path.join(printed_dir, f))
                    for pg in range(len(doc)):
                        pix = doc[pg].get_pixmap(dpi=200)
                        img_bytes = pix.tobytes("png")
                        docs.append({
                            "name": os.path.splitext(f)[0],
                            "bytes": img_bytes,
                            "category": "printed",
                        })
                    doc.close()
        except ImportError:
            print("WARNING: PyMuPDF not installed, skipping PDFs")

    return docs


def run_local_fallback():
    """Run with a local placeholder if Modal is not available."""
    print("WARNING: Running in local fallback mode (no GPU)")
    print("GLM-OCR requires Modal GPU. Generating placeholder results.")

    docs = get_test_images()
    results = {
        "model": "glm_ocr",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "note": "LOCAL FALLBACK - no actual OCR performed. Run on Modal for real results.",
        "documents": [],
    }

    for doc in docs:
        results["documents"].append({
            "name": doc["name"],
            "category": doc["category"],
            "ocr_text": "[GLM-OCR requires Modal GPU - placeholder result]",
            "latency_s": 0.0,
            "status": "placeholder",
        })

    out = os.path.join(RESULTS_DIR, "glm_ocr_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Placeholder results saved to {out}")


def main():
    if HAS_MODAL:
        print("Running GLM-OCR on Modal GPU...")
        docs = get_test_images()
        print(f"Prepared {len(docs)} documents")

        with modal.enable_output():
            with app.run():
                modal_results = run_glm_ocr_modal.remote(docs)

        results = {
            "model": "glm_ocr",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "documents": modal_results,
        }

        out = os.path.join(RESULTS_DIR, "glm_ocr_results.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {out}")
    else:
        run_local_fallback()


if __name__ == "__main__":
    main()
