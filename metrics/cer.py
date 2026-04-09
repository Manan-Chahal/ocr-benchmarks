"""
Character Error Rate (CER), Word Error Rate (WER), and related metrics
for OCR benchmark evaluation.
"""

import re
import statistics
from typing import List, Optional

import Levenshtein


# ── Core metrics ─────────────────────────────────────────────────────────────

def character_error_rate(reference: str, hypothesis: str) -> float:
    """
    Compute Character Error Rate (CER).

    CER = edit_distance(ref, hyp) / len(ref)

    Returns 0.0 for a perfect match.  Can exceed 1.0 when the hypothesis
    is significantly longer or completely wrong.
    """
    if not reference:
        return 0.0 if not hypothesis else 1.0
    distance = Levenshtein.distance(reference, hypothesis)
    return distance / len(reference)


def word_error_rate(reference: str, hypothesis: str) -> float:
    """
    Compute Word Error Rate (WER) using dynamic programming.

    WER = word_edit_distance(ref, hyp) / len(ref_words)
    """
    ref_words = reference.split()
    hyp_words = hypothesis.split()

    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    m, n = len(ref_words), len(hyp_words)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],       # deletion
                    dp[i][j - 1],       # insertion
                    dp[i - 1][j - 1],   # substitution
                )

    return dp[m][n] / m


def accuracy(reference: str, hypothesis: str) -> float:
    """Character-level accuracy: ``max(0, 1 − CER)``."""
    return max(0.0, 1.0 - character_error_rate(reference, hypothesis))


# ── Extended metrics ─────────────────────────────────────────────────────────

def char_precision_recall_f1(reference: str, hypothesis: str):
    """
    Character-level precision, recall, and F1 based on Levenshtein ops.

    * **Precision** = correct_chars / len(hypothesis)
    * **Recall**    = correct_chars / len(reference)
    * **F1**        = harmonic mean of precision and recall

    Returns ``(precision, recall, f1)`` as floats in [0, 1].
    """
    if not reference and not hypothesis:
        return (1.0, 1.0, 1.0)
    if not reference:
        return (0.0, 1.0, 0.0)
    if not hypothesis:
        return (0.0, 0.0, 0.0)

    ops = Levenshtein.editops(reference, hypothesis)

    substitutions = sum(1 for op, *_ in ops if op == "replace")
    deletions = sum(1 for op, *_ in ops if op == "delete")
    insertions = sum(1 for op, *_ in ops if op == "insert")

    correct = len(reference) - substitutions - deletions

    precision = correct / len(hypothesis) if len(hypothesis) > 0 else 0.0
    recall = correct / len(reference) if len(reference) > 0 else 0.0

    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)

    return (
        max(0.0, min(1.0, precision)),
        max(0.0, min(1.0, recall)),
        max(0.0, min(1.0, f1)),
    )


# ── Aggregate helpers ────────────────────────────────────────────────────────

def median_value(values: List[float]) -> Optional[float]:
    """Return median, or None for empty lists."""
    if not values:
        return None
    return statistics.median(values)


def is_outlier(value: float, mean: float, *, factor: float = 2.0) -> bool:
    """Return True when *value* exceeds *factor* × *mean*."""
    return value > factor * mean


# ── Text normalisation ───────────────────────────────────────────────────────

def normalize_text(text: str) -> str:
    """Lowercase, strip, and collapse whitespace for fair comparison."""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


# ── Self-test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ref = "The quick brown fox jumps over the lazy dog"
    hyp = "The quik brown fox jumps over the lasy dog"

    print(f"Reference:  {ref}")
    print(f"Hypothesis: {hyp}")
    print(f"CER:        {character_error_rate(ref, hyp):.4f}")
    print(f"WER:        {word_error_rate(ref, hyp):.4f}")
    print(f"Accuracy:   {accuracy(ref, hyp):.4f}")

    p, r, f = char_precision_recall_f1(ref, hyp)
    print(f"Precision:  {p:.4f}")
    print(f"Recall:     {r:.4f}")
    print(f"F1:         {f:.4f}")
