# OCR Model Benchmarking Report

**Date:** 2026-04-06 15:07:31
**Models:** easyocr, glm_ocr, paddleocr_vl, qwen25_vl, olmocr2

---

## Summary Comparison

| Model | Avg CER | Avg WER | Avg Accuracy | Avg Latency (s) | Docs Tested | Languages |
|-------|---------|---------|-------------|-----------------|-------------|-----------|
| easyocr | 0.2458 | 0.5120 | 75.42% | 6.114 | 16 | en, es, fr |
| glm_ocr | N/A | N/A | N/A | N/A | 0 | N/A |
| paddleocr_vl | N/A | N/A | N/A | N/A | 0 | N/A |
| qwen25_vl | N/A | N/A | N/A | N/A | 0 | N/A |
| olmocr2 | N/A | N/A | N/A | N/A | 0 | N/A |

---

## Detailed Results by Model

### easyocr

- **Average CER:** 0.2458
- **Average WER:** 0.512
- **Average Accuracy:** 75.42%
- **Average Latency:** 6.114s
- **Languages:** en, es, fr

| Document | Language | CER | WER | Accuracy | Latency (s) |
|----------|----------|-----|-----|----------|-------------|
| en_form_001.png | en | 0.2981 | 0.6682 | 70.19% | 7.944 |
| en_form_002.png | en | 0.5844 | 0.7605 | 41.56% | 4.984 |
| en_form_003.png | en | 0.2778 | 0.6402 | 72.22% | 6.539 |
| en_form_004.png | en | 0.2619 | 0.7297 | 73.81% | 5.773 |
| en_form_005.png | en | 0.4198 | 0.6018 | 58.02% | 4.79 |
| en_receipt_001.jpg | en | 0.2969 | 0.7294 | 70.31% | 3.734 |
| en_receipt_002.jpg | en | 0.2836 | 0.5294 | 71.64% | 3.296 |
| en_receipt_003.jpg | en | 0.1895 | 0.5935 | 81.05% | 4.039 |
| en_receipt_004.jpg | en | 0.3647 | 0.7429 | 63.53% | 4.168 |
| en_receipt_005.jpg | en | 0.3338 | 0.8264 | 66.62% | 5.115 |
| en_iam_001.png | en | 0.0164 | 0.087 | 98.36% | 1.715 |
| en_iam_002.png | en | 0.0282 | 0.1316 | 97.18% | 2.137 |
| en_iam_003.png | en | 0.0263 | 0.0789 | 97.37% | 2.02 |
| en_payroll_register | en | 0.1599 | 0.3952 | 84.01% | 13.693 |
| es_factura | es | 0.1397 | 0.274 | 86.03% | 13.472 |
| fr_rapport_medical | fr | 0.2516 | 0.403 | 74.84% | 14.408 |

### glm_ocr

*No results available for this model.*

### paddleocr_vl

*No results available for this model.*

### qwen25_vl

*No results available for this model.*

### olmocr2

*No results available for this model.*

---

## Recommendation

- **Highest Accuracy:** `easyocr` (75.42% avg)
- **Fastest Processing:** `easyocr` (6.114s avg)

**Primary Recommendation:** `easyocr` - Best in both accuracy and speed.
