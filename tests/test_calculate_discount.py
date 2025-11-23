def calculate_discount(price: float, discount: float) -> float:
    if discount < 0 or discount > 1:
        raise ValueError("discount must be between 0 and 1")

    return price * (1 - discount)


def test_calculate_discount():
    assert calculate_discount(100, 0.2) == 80
    assert calculate_discount(50, 0) == 50
    assert calculate_discount(200, 1) == 0

    try:
        calculate_discount(100.0, -0.1)
    except ValueError as e:
        assert str(e) == "discount must be between 0 and 1"

    try:
        calculate_discount(100.0, 1.5)
    except ValueError as e:
        assert str(e) == "discount must be between 0 and 1"
