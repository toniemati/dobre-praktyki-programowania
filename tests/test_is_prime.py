import math


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    limit = math.isqrt(n)
    
    i = 3
    while i <= limit:
        if n % i == 0:
            return False
        i += 2
    return True


def test_is_prime():
    assert is_prime(2) is True
    assert is_prime(3) is True
    assert is_prime(4) is False
    assert is_prime(0) is False
    assert is_prime(1) is False
    assert is_prime(5) is True
    assert is_prime(97) is True
   