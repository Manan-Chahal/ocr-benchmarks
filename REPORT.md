# OCR Model Benchmarking Report

**Date:** 2026-04-06 15:48:13
**Models:** easyocr, glm_ocr, paddleocr_vl, qwen25_vl, olmocr2

---

## Summary Comparison

| Model | Avg CER | Avg WER | Avg Accuracy | Avg Latency (s) | Docs Tested | Languages |
|-------|---------|---------|-------------|-----------------|-------------|-----------|
| easyocr | 0.2458 | 0.5120 | 75.42% | 6.114 | 16 | en, es, fr |
| glm_ocr | 0.2192 | 0.3163 | 79.49% | 18.347 | 16 | en, es, fr |
| paddleocr_vl | N/A | N/A | N/A | N/A | 0 | N/A |
| qwen25_vl | 0.1312 | 0.2058 | 86.88% | 13.196 | 16 | en, es, fr |
| olmocr2 | 0.5656 | 0.8745 | 58.58% | 18.822 | 16 | en, es, fr |

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

- **Average CER:** 0.2192
- **Average WER:** 0.3163
- **Average Accuracy:** 79.49%
- **Average Latency:** 18.347s
- **Languages:** en, es, fr

| Document | Language | CER | WER | Accuracy | Latency (s) |
|----------|----------|-----|-----|----------|-------------|
| en_form_001.png | en | 0.168 | 0.2691 | 83.20% | 23.808 |
| en_form_002.png | en | 0.9473 | 1.0838 | 5.27% | 19.694 |
| en_form_003.png | en | 0.1562 | 0.2944 | 84.38% | 22.099 |
| en_form_004.png | en | 0.2889 | 0.4414 | 71.11% | 20.382 |
| en_form_005.png | en | 1.2264 | 1.6283 | 0.00% | 17.553 |
| en_receipt_001.jpg | en | 0.0639 | 0.2588 | 93.61% | 14.532 |
| en_receipt_002.jpg | en | 0.1988 | 0.2353 | 80.12% | 16.88 |
| en_receipt_003.jpg | en | 0.0028 | 0.0163 | 99.72% | 22.851 |
| en_receipt_004.jpg | en | 0.0942 | 0.2095 | 90.58% | 16.253 |
| en_receipt_005.jpg | en | 0.0251 | 0.1389 | 97.49% | 25.41 |
| en_iam_001.png | en | 0.0 | 0.0 | 100.00% | 4.525 |
| en_iam_002.png | en | 0.0 | 0.0 | 100.00% | 5.519 |
| en_iam_003.png | en | 0.0 | 0.0 | 100.00% | 6.033 |
| en_payroll_register | en | 0.1078 | 0.2216 | 89.22% | 26.665 |
| es_factura | es | 0.1002 | 0.089 | 89.98% | 23.62 |
| fr_rapport_medical | fr | 0.1276 | 0.1741 | 87.24% | 27.731 |

### paddleocr_vl

*No results available for this model.*

### qwen25_vl

- **Average CER:** 0.1312
- **Average WER:** 0.2058
- **Average Accuracy:** 86.88%
- **Average Latency:** 13.196s
- **Languages:** en, es, fr

| Document | Language | CER | WER | Accuracy | Latency (s) |
|----------|----------|-----|-----|----------|-------------|
| en_form_001.png | en | 0.1465 | 0.2735 | 85.35% | 16.531 |
| en_form_002.png | en | 0.5305 | 0.6048 | 46.95% | 14.627 |
| en_form_003.png | en | 0.1554 | 0.2944 | 84.46% | 13.922 |
| en_form_004.png | en | 0.2205 | 0.4279 | 77.95% | 13.361 |
| en_form_005.png | en | 0.3853 | 0.5044 | 61.47% | 9.491 |
| en_receipt_001.jpg | en | 0.0763 | 0.2706 | 92.37% | 9.533 |
| en_receipt_002.jpg | en | 0.1082 | 0.1765 | 89.18% | 11.832 |
| en_receipt_003.jpg | en | 0.0124 | 0.065 | 98.76% | 16.278 |
| en_receipt_004.jpg | en | 0.0771 | 0.1524 | 92.29% | 11.329 |
| en_receipt_005.jpg | en | 0.0326 | 0.1875 | 96.74% | 18.83 |
| en_iam_001.png | en | 0.0 | 0.0 | 100.00% | 1.427 |
| en_iam_002.png | en | 0.0 | 0.0 | 100.00% | 1.924 |
| en_iam_003.png | en | 0.0 | 0.0 | 100.00% | 2.569 |
| en_payroll_register | en | 0.1448 | 0.1317 | 85.52% | 24.873 |
| es_factura | es | 0.0991 | 0.0753 | 90.09% | 21.029 |
| fr_rapport_medical | fr | 0.1103 | 0.1294 | 88.97% | 23.58 |

### olmocr2

- **Average CER:** 0.5656
- **Average WER:** 0.8745
- **Average Accuracy:** 58.58%
- **Average Latency:** 18.822s
- **Languages:** en, es, fr

| Document | Language | CER | WER | Accuracy | Latency (s) |
|----------|----------|-----|-----|----------|-------------|
| en_form_001.png | en | 0.3123 | 0.4753 | 68.77% | 16.308 |
| en_form_002.png | en | 0.7246 | 0.7844 | 27.54% | 16.768 |
| en_form_003.png | en | 0.244 | 0.4065 | 75.60% | 15.39 |
| en_form_004.png | en | 0.3002 | 0.4459 | 69.98% | 15.271 |
| en_form_005.png | en | 3.4228 | 7.292 | 0.00% | 74.343 |
| en_receipt_001.jpg | en | 0.6412 | 0.8706 | 35.88% | 6.623 |
| en_receipt_002.jpg | en | 0.5073 | 0.6765 | 49.27% | 15.159 |
| en_receipt_003.jpg | en | 0.7248 | 0.8862 | 27.52% | 20.22 |
| en_receipt_004.jpg | en | 0.6301 | 0.8286 | 36.99% | 15.266 |
| en_receipt_005.jpg | en | 0.611 | 0.6806 | 38.90% | 20.867 |
| en_iam_001.png | en | 0.0 | 0.0 | 100.00% | 1.395 |
| en_iam_002.png | en | 0.0 | 0.0 | 100.00% | 1.889 |
| en_iam_003.png | en | 0.0 | 0.0 | 100.00% | 2.529 |
| en_payroll_register | en | 0.3499 | 0.1557 | 65.01% | 28.518 |
| es_factura | es | 0.3124 | 0.2466 | 68.76% | 24.086 |
| fr_rapport_medical | fr | 0.2689 | 0.2438 | 73.11% | 26.513 |

---

## Recommendation

- **Highest Accuracy:** `qwen25_vl` (86.88% avg)
- **Fastest Processing:** `easyocr` (6.114s avg)

**Primary Recommendation:** `qwen25_vl` for accuracy-critical workloads.
**Secondary Recommendation:** `easyocr` for throughput-critical workloads.
