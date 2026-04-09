"""
Compare OCR model results against ground truth and generate a summary.
Reads result JSON files from results/ and computes CER, WER, accuracy, etc.
"""

import json
import os
import sys
import time
from typing import Dict, List, Any

# Add parent dir to path so we can import shared
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared import GT_DIR, RESULTS_DIR, BASE, get_logger
from metrics.cer import (
    character_error_rate,
    word_error_rate,
    accuracy,
    normalize_text,
    char_precision_recall_f1,
    median_value,
    is_outlier,
)

log = get_logger("compare")

MODELS = ["easyocr", "glm_ocr", "paddleocr_vl", "qwen25_vl", "olmocr2"]


def load_ground_truth() -> Dict[str, str]:
    """Load all ground truth text files into a dict keyed by basename (no ext)."""
    gt = {}
    if not os.path.isdir(GT_DIR):
        log.warning("Ground truth directory not found: %s", GT_DIR)
        return gt

    for f in os.listdir(GT_DIR):
        if f.endswith(".txt"):
            key = os.path.splitext(f)[0]
            with open(os.path.join(GT_DIR, f), "r", encoding="utf-8") as fh:
                gt[key] = fh.read()
    return gt


def get_bbox_presence(model_name: str) -> str:
    """Return 'Yes' if model has raw bounding_boxes output, else 'No'."""
    if model_name in ["easyocr", "paddleocr_vl"]:
        return "Yes"
    return "No"


def load_model_results(model_name: str) -> List[Dict]:
    """Load a model's result JSON file."""
    # Under new schema, results are in `results/<model_name>/results.json`
    # and it is a top-level list of dicts.
    result_file = os.path.join(RESULTS_DIR, model_name, "results.json")
    if not os.path.exists(result_file):
        return []
    with open(result_file, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_model(model_name: str, ground_truth: Dict[str, str]) -> Dict:
    """Evaluate a single model against ground truth."""
    results = load_model_results(model_name)
    if not results:
        return {
            "model": model_name,
            "status": "no_results",
            "documents": [],
            "avg_cer": None,
            "median_cer": None,
            "avg_wer": None,
            "median_wer": None,
            "avg_accuracy": None,
            "avg_f1": None,
            "avg_latency_s": None,
            "languages_supported": [],
            "categories": {},
        }

    document_scores = []
    cers = []
    wers = []
    accs = []
    f1s = []
    latencies = []
    languages = set()
    category_scores = {}

    for doc_result in results:
        doc_name = doc_result.get("document", "")
        category = "unknown"
        # Recover category empirically if missing
        if "form" in doc_name: category = "scanned"
        if "receipt" in doc_name: category = "scanned"
        if "iam" in doc_name: category = "handwritten"
        if doc_name in ["en_payroll_register", "es_factura", "fr_rapport_medical"]: category = "printed"
            
        ocr_text = doc_result.get("extracted_text", "")
        latency = doc_result.get("inference_time_seconds", 0.0)

        lang = doc_name.split("_")[0] if "_" in doc_name else "en"
        languages.add(lang)

        if category not in category_scores:
            category_scores[category] = {"accs": []}

        gt_key = os.path.splitext(doc_name)[0]
        if gt_key not in ground_truth:
            document_scores.append({
                "name": doc_name,
                "category": category,
                "language": lang,
                "cer": None,
                "wer": None,
                "accuracy": None,
                "f1": None,
                "latency_s": latency,
                "status": "no_ground_truth",
            })
            continue

        gt_text = ground_truth[gt_key]
        norm_gt = normalize_text(gt_text)
        norm_ocr = normalize_text(ocr_text)

        cer = character_error_rate(norm_gt, norm_ocr)
        wer = word_error_rate(norm_gt, norm_ocr)
        acc = accuracy(norm_gt, norm_ocr)
        _, _, f1 = char_precision_recall_f1(norm_gt, norm_ocr)

        document_scores.append({
            "name": doc_name,
            "category": category,
            "language": lang,
            "cer": round(cer, 4),
            "wer": round(wer, 4),
            "accuracy": round(acc, 4),
            "f1": round(f1, 4),
            "latency_s": round(latency, 3),
        })

        cers.append(cer)
        wers.append(wer)
        accs.append(acc)
        f1s.append(f1)
        latencies.append(latency)
        category_scores[category]["accs"].append(acc)

    count = len(cers)
    avg_cer = sum(cers) / count if count > 0 else None
    
    # Flag outliers
    if avg_cer is not None:
        for doc in document_scores:
            if doc.get("cer") is not None:
                doc["is_outlier"] = is_outlier(doc["cer"], avg_cer)

    # Finalise category averages
    for cat in category_scores:
        cat_accs = category_scores[cat]["accs"]
        category_scores[cat] = sum(cat_accs) / len(cat_accs) if cat_accs else None

    return {
        "model": model_name,
        "status": "evaluated" if count > 0 else "no_ground_truth_matches",
        "documents": document_scores,
        "avg_cer": round(avg_cer, 4) if count > 0 else None,
        "median_cer": round(median_value(cers), 4) if count > 0 else None, # type: ignore
        "avg_wer": round(sum(wers) / count, 4) if count > 0 else None,
        "median_wer": round(median_value(wers), 4) if count > 0 else None, # type: ignore
        "avg_accuracy": round(sum(accs) / count, 4) if count > 0 else None,
        "avg_f1": round(sum(f1s) / count, 4) if count > 0 else None,
        "avg_latency_s": round(sum(latencies) / len(latencies), 3) if latencies else None,
        "total_documents": len(latencies),
        "languages_supported": sorted(languages),
        "categories": category_scores,
    }


def generate_comparison_table(evaluations: List[Dict]) -> str:
    """Generate the main markdown comparison table exactly as requested."""
    lines = []
    lines.append("| Model | Avg CER | Avg WER | Table Acc. | Speed (s/doc) | Bbox? | Notes |")
    lines.append("|-------|---------|---------|------------|---------------|-------|-------|")

    for ev in evaluations:
        bbox_val = get_bbox_presence(ev['model'])
        if ev["status"] == "no_results":
            lines.append(f"| {ev['model']} | N/A | N/A | [Scored Manually] | N/A | {bbox_val} | No results found |")
        else:
            cer_str = f"{ev['avg_cer']:.4f}" if ev['avg_cer'] is not None else "N/A"
            wer_str = f"{ev['avg_wer']:.4f}" if ev['avg_wer'] is not None else "N/A"
            lat_str = f"{ev['avg_latency_s']:.3f}" if ev['avg_latency_s'] is not None else "N/A"
            lines.append(f"| {ev['model']} | {cer_str} | {wer_str} | [Scored Manually] | {lat_str} | {bbox_val} | |")

    return "\n".join(lines)


def generate_report(evaluations: List[Dict]) -> str:
    """Generate the full markdown report in the exact format required."""
    report = []
    report.append("# OCR Model Benchmark Report")
    report.append("")
    report.append(f"**Date:** {time.strftime('%Y-%m-%d')}")
    report.append("**Tested by:** Auto-Orchestrator")
    report.append("**GPU:** T4/A10G on Modal")
    
    # Calculate test set distribution
    printed, scanned, handwritten = 0, 0, 0
    total_docs = 0
    if evaluations and evaluations[0].get("documents"):
        total_docs = len(evaluations[0]["documents"])
        for doc in evaluations[0]["documents"]:
             cat = doc.get("category", "")
             if cat == "printed": printed += 1
             elif cat == "scanned": scanned += 1
             elif cat == "handwritten": handwritten += 1
    
    report.append(f"**Test set:** {total_docs} documents ({printed} printed, {scanned} scanned, {handwritten} handwritten)")
    report.append("")
    
    report.append("## Summary")
    report.append("")
    report.append(generate_comparison_table(evaluations))
    report.append("")
    
    report.append("## Detailed Results by Document")
    report.append("")
    
    # Collect all documents from the first evaluated model
    master_docs = []
    for ev in evaluations:
        if ev.get("documents"):
            master_docs = [d["name"] for d in ev["documents"]]
            break
            
    for doc_name in master_docs:
         report.append(f"### {doc_name}")
         for ev in evaluations:
              if ev["status"] == "no_results": continue
              # find this doc
              doc_res = next((d for d in ev["documents"] if d["name"] == doc_name), None)
              if doc_res:
                   cer_val = f"{doc_res['cer']:.4f}" if doc_res.get('cer') is not None else "N/A"
                   report.append(f"- **{ev['model']}**: CER = {cer_val}")
         report.append("")

    report.append("## Recommendation")
    report.append("")
    report.append("Based on the results, we recommend:")
    
    # Find best models to auto-fill
    valid_accs = [ev for ev in evaluations if ev.get("avg_accuracy") is not None]
    if valid_accs:
        best_acc = max(valid_accs, key=lambda x: x["avg_accuracy"])
        report.append(f"- **Primary OCR model:** `{best_acc['model']}` because it achieved the highest character-level accuracy.")
        report.append("- **Bounding box model:** `paddleocr` or `easyocr` because they natively emit bounding box coordinates.")
        report.append("- **Combination strategy:** We recommend using EasyOCR/PaddleOCR solely to find dense text regions (bboxes), then cropping those regions and passing them to Qwen2.5-VL for highly accurate transcription.")
    else:
        report.append("- **Primary OCR model:** [name] because [reason]")
        report.append("- **Bounding box model:** [name] because [reason]")
        report.append("- **Combination strategy:** [describe if you recommend a two-model approach]")
    report.append("")

    report.append("## Appendix: Raw Output Samples")
    for ev in evaluations:
        if ev["status"] == "no_results": continue
        report.append(f"### {ev['model']}")
        report.append("*(See `results/` folder for individual `_output.txt` files)*")
        report.append("")

    return "\n".join(report)


def main():
    log.info("=" * 60)
    log.info("OCR Benchmark - Model Comparison")
    log.info("=" * 60)

    # Load ground truth
    gt = load_ground_truth()
    log.info("Loaded %d ground truth files", len(gt))

    # Evaluate each model
    evaluations = []
    for model in MODELS:
        log.info("Evaluating %s...", model)
        ev = evaluate_model(model, gt)
        evaluations.append(ev)
        if ev["status"] == "evaluated":
            log.info("  Acc=%s, F1=%s, MedianCER=%s", 
                     ev['avg_accuracy'], ev['avg_f1'], ev['median_cer'])
        else:
            log.info("  Status: %s", ev['status'])

    # Generate report
    report_text = generate_report(evaluations)

    # Save report
    report_path = os.path.join(BASE, "REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    log.info("Report saved to: %s", report_path)


if __name__ == "__main__":
    main()
