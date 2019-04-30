import csv
import os
from itertools import chain

def hashdigit(cnpj, position):  # type: (str, int) -> int
    """
    Will compute the given `position` checksum digit for the `cnpj`
    input. The input needs to contain all elements previous to
    `position` else computation will yield the wrong result.
    """
    weightgen = chain(range(position -8, 1, -1), range(9, 1, -1))
    val = sum(int(digit) * weight for digit, weight in zip(cnpj, weightgen)) % 11
    return 0 if val < 2 else 11 - val

def cnpj_isvalid(cnpj):  # type: (str) -> bool
    """
    Returns whether or not the verifying checksum digits of the
    given `cnpj` match it's base number. Input should be a digit
    string of proper length.
    """
    if not cnpj.isdigit() or len(cnpj) != 14 or len(set(cnpj)) == 1: return False
    return all(hashdigit(cnpj, i +13) == int(v) for i, v in enumerate(cnpj[12:]))

def cpf_isvalid(cpf_string):
    if not cpf_string.isdigit():
        return False
    if len(cpf_string) != 11:
        return False
    numbers = [int(digit) for digit in cpf_string if digit.isdigit()]
    # Validação do primeiro dígito verificador:
    sum_of_products = sum(a*b for a, b in zip(numbers[0:9], range(10, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[9] != expected_digit:
        return False
    # Validação do segundo dígito verificador:
    sum_of_products = sum(a*b for a, b in zip(numbers[0:10], range(11, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[10] != expected_digit:
        return False
    return True
