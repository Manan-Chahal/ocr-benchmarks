"""
Shared utilities for the OCR benchmarking suite.
Centralises constants, image loading, and result saving to avoid duplication.
"""

import json
import logging
import os
import time
from typing import Dict, List, Optional

# ── Paths ────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE, "results")
GT_DIR = os.path.join(BASE, "ground_truth")
TEST_DOCS_DIR = os.path.join(BASE, "test_documents")

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tiff", ".bmp")

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_FMT = "%(asctime)s │ %(name)-14s │ %(levelname)-7s │ %(message)s"
LOG_DATE_FMT = "%H:%M:%S"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a consistently-formatted logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FMT, datefmt=LOG_DATE_FMT))
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


# ── Image collection ─────────────────────────────────────────────────────────

def get_test_images(*, as_bytes: bool = False) -> List[Dict]:
    """
    Collect all test document paths (or bytes) from test_documents/.

    Parameters
    ----------
    as_bytes : bool
        If True, read file contents into ``item["bytes"]`` (needed for
        Modal-based runners that serialise images to the remote GPU).
        If False, ``item["path"]`` contains the local filesystem path.

    Returns
    -------
    list[dict]
        Each dict has keys: name, category, and either path or bytes.
    """
    log = get_logger("shared")
    docs: List[Dict] = []

    for subdir in ("scanned", "handwritten"):
        folder = os.path.join(TEST_DOCS_DIR, subdir)
        if not os.path.isdir(folder):
            log.debug("Skipping missing folder: %s", folder)
            continue
        for fname in sorted(os.listdir(folder)):
            if not fname.lower().endswith(IMAGE_EXTENSIONS):
                continue
            full_path = os.path.join(folder, fname)
            entry: Dict = {"name": fname, "category": subdir}
            if as_bytes:
                with open(full_path, "rb") as fh:
                    entry["bytes"] = fh.read()
            else:
                entry["path"] = full_path
            docs.append(entry)

    # Printed PDFs → convert to images
    printed_dir = os.path.join(TEST_DOCS_DIR, "printed")
    if os.path.isdir(printed_dir):
        try:
            import fitz  # PyMuPDF
        except ImportError:
            log.warning("PyMuPDF not installed — skipping printed PDFs")
            fitz = None  # type: ignore[assignment]

        if fitz is not None:
            for fname in sorted(os.listdir(printed_dir)):
                if not fname.lower().endswith(".pdf"):
                    continue
                pdf_path = os.path.join(printed_dir, fname)
                try:
                    doc = fitz.open(pdf_path)
                    for page_num in range(len(doc)):
                        page = doc[page_num]
                        pix = page.get_pixmap(dpi=200)
                        base_name = os.path.splitext(fname)[0]
                        entry = {"name": base_name, "category": "printed"}
                        if as_bytes:
                            entry["bytes"] = pix.tobytes("png")
                        else:
                            img_path = os.path.join(
                                printed_dir,
                                f"{base_name}_p{page_num}.png",
                            )
                            pix.save(img_path)
                            entry["path"] = img_path
                        docs.append(entry)
                    doc.close()
                except Exception:
                    log.exception("Failed to process PDF: %s", pdf_path)

    log.info("Collected %d test documents", len(docs))
    return docs


# ── Result saving ────────────────────────────────────────────────────────────

def save_results(
    model_name: str,
    documents: List[Dict],
    *,
    extra_meta: Optional[Dict] = None,
) -> str:
    """
    Persist model results to ``results/<model_name>/results.json``.
    Also write individual text outputs to ``results/<model_name>/<doc>_output.txt``.
    """
    model_dir = os.path.join(RESULTS_DIR, model_name)
    os.makedirs(model_dir, exist_ok=True)
    
    # Optional conversion of old keys to correct employee guide keys
    cleaned_docs = []
    for doc in documents:
        # Avoid mutating the original caller's dictionary directly
        new_doc = doc.copy()
        
        # Guide expects 'document' instead of 'name'
        if "name" in new_doc and "document" not in new_doc:
            new_doc["document"] = new_doc.pop("name")
            
        # Guide expects 'extracted_text' instead of 'ocr_text'
        if "ocr_text" in new_doc and "extracted_text" not in new_doc:
            new_doc["extracted_text"] = new_doc.pop("ocr_text")
            
        # Guide expects 'inference_time_seconds' instead of 'latency_s'
        if "latency_s" in new_doc and "inference_time_seconds" not in new_doc:
            new_doc["inference_time_seconds"] = new_doc.pop("latency_s")
            
        # Ensure Bounding box key exists
        if "bounding_boxes" not in new_doc:
            new_doc["bounding_boxes"] = None
            
        # Ensure detected_language exists
        if "detected_language" not in new_doc:
             new_doc["detected_language"] = None
             
        # Ensure notes exist
        if "notes" not in new_doc:
            new_doc["notes"] = ""
            
        if "gpu" not in new_doc:
            new_doc["gpu"] = "T4" # default or pass in extra_meta
            
        cleaned_docs.append(new_doc)
    
    payload: Dict = cleaned_docs
    if extra_meta:
        # Wrap everything in a list? Wait, the guide code saves `results` directly as JSON.
        # "with open(..., "w") as f: json.dump(results, f)"
        pass

    out_path = os.path.join(model_dir, "results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_docs, f, indent=2, ensure_ascii=False)

    # Save individual text outputs
    for doc in cleaned_docs:
        doc_name = doc["document"].rsplit(".", 1)[0]
        text_out_path = os.path.join(model_dir, f"{doc_name}_output.txt")
        with open(text_out_path, "w", encoding="utf-8") as f:
             f.write(doc.get("extracted_text", ""))

    get_logger("shared").info("Results saved → %s", model_dir)
    return model_dir
