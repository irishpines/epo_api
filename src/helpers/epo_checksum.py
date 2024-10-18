import pytest


def luhn_checksum(epo_application_number: str) -> str:
    """
    Luhn_checksum determines the Luhn checksum or checkdigit of a string. as used by EPO
    """

    #  Licensing:
    #
    #    This code is distributed under the GNU LGPL license.
    #
    #  Modified:
    #
    #    08 September 2015
    #
    #  Reference:
    #
    #    https://en.wikipedia.org/wiki/Luhn_algorithm
    #
    #  Parameters:
    #
    #    Input, string CARD_NUMBER, the string of digits to be checked.
    #
    #    Output, integer VALUE, is the Luhn checksum for this string.
    #
    #  Source: https://people.math.sc.edu/Burkardt/py_src/luhn/luhn.py
    #
    assert (
        len(epo_application_number) == 8
    ), f"Calculating checksum, expected an eight digit number, got {epo_application_number}"

    def digits_of(n):
        return [int(d) for d in str(n)]

    digits = digits_of(epo_application_number)
    odd_digits = digits[0::2]
    even_digits = digits[1::2]

    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))

    value = 10 - (checksum % 10)
    if value == 10:
        return 0
    return value


def add_check_digit(epo_application_number: str) -> str:
    return f"{epo_application_number}.{luhn_checksum(epo_application_number)}"
