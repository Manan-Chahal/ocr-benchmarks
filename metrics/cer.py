"""
Character Error Rate (CER) and Word Error Rate (WER) computation
for OCR benchmark evaluation.
"""

import Levenshtein


def character_error_rate(reference: str, hypothesis: str) -> float:
    """
    Compute Character Error Rate (CER).
    CER = edit_distance(ref, hyp) / len(ref)
    Returns a float between 0.0 (perfect) and 1.0+ (very bad).
    """
    if not reference:
        return 0.0 if not hypothesis else 1.0
    distance = Levenshtein.distance(reference, hypothesis)
    return distance / len(reference)


def word_error_rate(reference: str, hypothesis: str) -> float:
    """
    Compute Word Error Rate (WER).
    WER = edit_distance(ref_words, hyp_words) / len(ref_words)
    Returns a float between 0.0 (perfect) and 1.0+ (very bad).
    """
    ref_words = reference.split()
    hyp_words = hypothesis.split()

    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    # Dynamic programming for word-level edit distance
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
                    dp[i - 1][j],      # deletion
                    dp[i][j - 1],      # insertion
                    dp[i - 1][j - 1],  # substitution
                )

    return dp[m][n] / m


def accuracy(reference: str, hypothesis: str) -> float:
    """Compute character-level accuracy as 1 - CER (clamped to 0)."""
    return max(0.0, 1.0 - character_error_rate(reference, hypothesis))


def normalize_text(text: str) -> str:
    """Normalize text for fair comparison: lowercase, collapse whitespace."""
    import re
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    return text


if __name__ == "__main__":
    # Quick self-test
    ref = "The quick brown fox jumps over the lazy dog"
    hyp = "The quik brown fox jumps over the lasy dog"

    print(f"Reference: {ref}")
    print(f"Hypothesis: {hyp}")
    print(f"CER: {character_error_rate(ref, hyp):.4f}")
    print(f"WER: {word_error_rate(ref, hyp):.4f}")
    print(f"Accuracy: {accuracy(ref, hyp):.4f}")
