import pytest
from helpers.epo_checksum import luhn_checksum, add_check_digit


@pytest.fixture(
    params=[
        "3661357",
        "18752141",
        "00650114",
        "24183680",
        "12781825",
    ],
)
def number(request):
    return request.param


def test_luhn_checksum(number):
    match number:
        case "3661357":
            with pytest.raises(AssertionError):
                luhn_checksum(number)
        case "18752141":
            assert luhn_checksum(number) == 4
        case "00650114":
            assert luhn_checksum(number) == 2
        case "24183680":
            assert luhn_checksum(number) == 8
        case "12781825":
            assert luhn_checksum(number) == 0


def test_add_check_digit(number):
    assert add_check_digit("18752141") == "18752141.4"
    assert add_check_digit("00650114") == "00650114.2"
