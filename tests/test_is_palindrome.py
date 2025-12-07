def is_palindrome(text: str) -> bool:
    cleaned = text.replace(" ", "").lower()

    return cleaned == cleaned[::-1]


def test_is_palindrome():
    assert is_palindrome('Kajak') is True
    assert is_palindrome('Kobyła ma mały bok') is True
    assert is_palindrome('python') is False
    assert is_palindrome('') is True
    assert is_palindrome('A') is True
