"""
Compare OCR model results against ground truth and generate a summary.
Reads result JSON files from results/ and computes CER, WER, accuracy, etc.
"""

import json
import os
import sys
import time
from typing import Dict, List

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from metrics.cer import character_error_rate, word_error_rate, accuracy, normalize_text


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE, "results")
GT_DIR = os.path.join(BASE, "ground_truth")

# The 5 models
MODELS = ["easyocr", "glm_ocr", "paddleocr_vl", "qwen25_vl", "olmocr2"]


def load_ground_truth() -> Dict[str, str]:
    """Load all ground truth text files into a dict keyed by basename (no ext)."""
    gt = {}
    for f in os.listdir(GT_DIR):
        if f.endswith(".txt"):
            key = os.path.splitext(f)[0]
            with open(os.path.join(GT_DIR, f), "r", encoding="utf-8") as fh:
                gt[key] = fh.read()
    return gt


def load_model_results(model_name: str) -> Dict:
    """Load a model's result JSON file."""
    result_file = os.path.join(RESULTS_DIR, f"{model_name}_results.json")
    if not os.path.exists(result_file):
        return {}
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
            "avg_wer": None,
            "avg_accuracy": None,
            "avg_latency_s": None,
            "languages_supported": [],
        }

    document_scores = []
    total_cer = 0.0
    total_wer = 0.0
    total_acc = 0.0
    total_latency = 0.0
    count = 0
    languages = set()

    for doc_result in results.get("documents", []):
        doc_name = doc_result.get("name", "")
        ocr_text = doc_result.get("ocr_text", "")
        latency = doc_result.get("latency_s", 0.0)

        # Determine language from filename
        lang = doc_name.split("_")[0] if "_" in doc_name else "en"
        languages.add(lang)

        # Find matching ground truth
        gt_key = os.path.splitext(doc_name)[0]
        if gt_key not in ground_truth:
            document_scores.append({
                "name": doc_name,
                "language": lang,
                "cer": None,
                "wer": None,
                "accuracy": None,
                "latency_s": latency,
                "status": "no_ground_truth",
            })
            continue

        gt_text = ground_truth[gt_key]

        # Normalize both for fair comparison
        norm_gt = normalize_text(gt_text)
        norm_ocr = normalize_text(ocr_text)

        cer = character_error_rate(norm_gt, norm_ocr)
        wer = word_error_rate(norm_gt, norm_ocr)
        acc = accuracy(norm_gt, norm_ocr)

        document_scores.append({
            "name": doc_name,
            "language": lang,
            "cer": round(cer, 4),
            "wer": round(wer, 4),
            "accuracy": round(acc, 4),
            "latency_s": round(latency, 3),
        })

        total_cer += cer
        total_wer += wer
        total_acc += acc
        total_latency += latency
        count += 1

    return {
        "model": model_name,
        "status": "evaluated",
        "documents": document_scores,
        "avg_cer": round(total_cer / count, 4) if count > 0 else None,
        "avg_wer": round(total_wer / count, 4) if count > 0 else None,
        "avg_accuracy": round(total_acc / count, 4) if count > 0 else None,
        "avg_latency_s": round(total_latency / count, 3) if count > 0 else None,
        "total_documents": count,
        "languages_supported": sorted(languages),
    }


def generate_comparison_table(evaluations: List[Dict]) -> str:
    """Generate a markdown comparison table."""
    lines = []
    lines.append("| Model | Avg CER | Avg WER | Avg Accuracy | Avg Latency (s) | Docs Tested | Languages |")
    lines.append("|-------|---------|---------|-------------|-----------------|-------------|-----------|")

    for ev in evaluations:
        if ev["status"] == "no_results":
            lines.append(f"| {ev['model']} | N/A | N/A | N/A | N/A | 0 | N/A |")
        else:
            cer_str = f"{ev['avg_cer']:.4f}" if ev['avg_cer'] is not None else "N/A"
            wer_str = f"{ev['avg_wer']:.4f}" if ev['avg_wer'] is not None else "N/A"
            acc_str = f"{ev['avg_accuracy']:.2%}" if ev['avg_accuracy'] is not None else "N/A"
            lat_str = f"{ev['avg_latency_s']:.3f}" if ev['avg_latency_s'] is not None else "N/A"
            langs = ", ".join(ev.get("languages_supported", []))
            lines.append(f"| {ev['model']} | {cer_str} | {wer_str} | {acc_str} | {lat_str} | {ev['total_documents']} | {langs} |")

    return "\n".join(lines)


def generate_report(evaluations: List[Dict]) -> str:
    """Generate the full markdown report."""
    report = []
    report.append("# OCR Model Benchmarking Report")
    report.append("")
    report.append(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Models:** {', '.join(MODELS)}")
    report.append("")
    report.append("---")
    report.append("")
    report.append("## Summary Comparison")
    report.append("")
    report.append(generate_comparison_table(evaluations))
    report.append("")
    report.append("---")
    report.append("")

    # Per-model details
    report.append("## Detailed Results by Model")
    report.append("")

    for ev in evaluations:
        report.append(f"### {ev['model']}")
        report.append("")
        if ev["status"] == "no_results":
            report.append("*No results available for this model.*")
            report.append("")
            continue

        report.append(f"- **Average CER:** {ev['avg_cer']}")
        report.append(f"- **Average WER:** {ev['avg_wer']}")
        report.append(f"- **Average Accuracy:** {ev['avg_accuracy']:.2%}" if ev['avg_accuracy'] else "- **Average Accuracy:** N/A")
        report.append(f"- **Average Latency:** {ev['avg_latency_s']}s" if ev['avg_latency_s'] else "- **Average Latency:** N/A")
        report.append(f"- **Languages:** {', '.join(ev.get('languages_supported', []))}")
        report.append("")

        # Document-level table
        report.append("| Document | Language | CER | WER | Accuracy | Latency (s) |")
        report.append("|----------|----------|-----|-----|----------|-------------|")
        for doc in ev["documents"]:
            if doc.get("status") == "no_ground_truth":
                report.append(f"| {doc['name']} | {doc['language']} | N/A | N/A | N/A | {doc.get('latency_s', 'N/A')} |")
            else:
                acc_str = f"{doc['accuracy']:.2%}" if doc.get('accuracy') is not None else "N/A"
                report.append(f"| {doc['name']} | {doc['language']} | {doc.get('cer', 'N/A')} | {doc.get('wer', 'N/A')} | {acc_str} | {doc.get('latency_s', 'N/A')} |")
        report.append("")

    # Recommendation
    report.append("---")
    report.append("")
    report.append("## Recommendation")
    report.append("")

    # Find best model by accuracy
    valid = [ev for ev in evaluations if ev["avg_accuracy"] is not None]
    if valid:
        best_accuracy = max(valid, key=lambda x: x["avg_accuracy"])
        best_speed = min(valid, key=lambda x: x["avg_latency_s"])
        report.append(f"- **Highest Accuracy:** `{best_accuracy['model']}` ({best_accuracy['avg_accuracy']:.2%} avg)")
        report.append(f"- **Fastest Processing:** `{best_speed['model']}` ({best_speed['avg_latency_s']:.3f}s avg)")
        report.append("")

        if best_accuracy['model'] == best_speed['model']:
            report.append(f"**Primary Recommendation:** `{best_accuracy['model']}` - Best in both accuracy and speed.")
        else:
            report.append(f"**Primary Recommendation:** `{best_accuracy['model']}` for accuracy-critical workloads.")
            report.append(f"**Secondary Recommendation:** `{best_speed['model']}` for throughput-critical workloads.")
    else:
        report.append("*No models have been evaluated yet. Run the benchmark runners first.*")

    report.append("")
    return "\n".join(report)


def main():
    print("=" * 60)
    print("OCR Benchmark - Model Comparison")
    print("=" * 60)

    # Load ground truth
    gt = load_ground_truth()
    print(f"\nLoaded {len(gt)} ground truth files")

    # Evaluate each model
    evaluations = []
    for model in MODELS:
        print(f"\nEvaluating {model}...")
        ev = evaluate_model(model, gt)
        evaluations.append(ev)
        if ev["status"] == "evaluated":
            print(f"  CER={ev['avg_cer']}, WER={ev['avg_wer']}, Accuracy={ev['avg_accuracy']}")
        else:
            print(f"  Status: {ev['status']}")

    # Generate report
    report_text = generate_report(evaluations)

    # Save report
    report_path = os.path.join(BASE, "REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\nReport saved to: {report_path}")

    # Also save comparison JSON
    comp_path = os.path.join(RESULTS_DIR, "comparison.json")
    with open(comp_path, "w", encoding="utf-8") as f:
        json.dump(evaluations, f, indent=2, ensure_ascii=False)
    print(f"Comparison data saved to: {comp_path}")


if __name__ == "__main__":
    main()
