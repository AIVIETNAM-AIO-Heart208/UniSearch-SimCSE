"""Prepare Vietnamese text for the PhoBERT tokenizer."""

import re
import unicodedata

_TONES = "\u0300\u0301\u0303\u0309\u0323"
_TONE_POSITION = re.compile(r"([oO][aAeE]|(?<![qQ])[uU][yY])([" + _TONES + r"])(?![^\W\d_])")


def normalize(text):
    decomposed = unicodedata.normalize("NFD", text)
    return unicodedata.normalize("NFC", _TONE_POSITION.sub(
        lambda match: match[1][0] + match[2] + match[1][1], decomposed
    ))


def segment(text):
    from pyvi import ViTokenizer

    return ViTokenizer.tokenize(normalize(text))
