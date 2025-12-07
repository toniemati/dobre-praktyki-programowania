def flatten_list(nested_list: list) -> list:
    result = []

    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)

    return result


def test_flatten_list():
    assert flatten_list([1, 2, 3]) == [1, 2, 3]
    assert flatten_list([1, [2, 3], [4, [5]]]) == [1, 2, 3, 4, 5]
    assert flatten_list([]) == []
    assert flatten_list([[[1]]]) == [1]
    assert flatten_list([1, [2, [3, [4]]]]) == [1, 2, 3, 4]
