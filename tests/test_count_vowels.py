def count_vowels(text: str) -> int:
    vowels = {'a', 'e', 'i', 'o', 'u', 'y'}
    
    return sum(1 for char in text.lower() if char in vowels)


def test_count_vowels():
    assert count_vowels("Python") == 2
    assert count_vowels("AEIOUY") == 6
    assert count_vowels("bcd") == 0
    assert count_vowels("") == 0
    assert count_vowels("Próba żółwia") == 3