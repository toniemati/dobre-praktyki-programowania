import re
from collections import Counter


def word_frequencies(text: str) -> dict:
    if not text:
        return {}

    words = re.findall(r"\b[\w']+\b", text.lower(), flags=re.UNICODE)

    return dict(Counter(words))


def test_basic_counts():
    assert word_frequencies('To be or not to be') == {
        "to": 2, "be": 2, "or": 1, "not": 1
    }
    assert word_frequencies('Hello, hello!') == {"hello": 2}
    assert word_frequencies('') == {}
    assert word_frequencies('Python python python') == {"python": 3}
    assert word_frequencies('Ala ma kota, a kot ma Ale.') == {
        "a": 1, "ala": 1, "ma": 2, "kota": 1, "kot": 1, "ale": 1
    }
