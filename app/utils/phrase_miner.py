# phrase_miner.py
import re

def extract_phrases(text: str):
    """
    Extract candidate phrases เช่น:
    - machine learning
    - spring boot
    - aws lambda
    """

    if not text:
        return []

    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    words = text.split()
    phrases = []

    # เอา bigram (2 คำติดกัน)
    for i in range(len(words) - 1):
        phrase = f"{words[i]} {words[i+1]}"
        phrases.append(phrase)

    return list(set(phrases))
