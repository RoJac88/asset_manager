import csv
import os
import io

from app import db
from flask_login import current_user
from app.models import NaturalPerson, LegalPerson
from itertools import chain
from datetime import datetime

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

def import_csv(fie_storage_obj, bom):
    encoding="utf8"
    if bom: encoding="utf_8_sig"
    print("Trying to import csv...")
    f = fie_storage_obj
    print(f)
    stream = io.StringIO(f.stream.read().decode(encoding), newline='')
    print(stream)
    reader = csv.DictReader(stream)
    added = 0
    for row in reader:
        data = dict(row)
        data =  {k.lower().replace('-','').replace('/','').replace('.',''): str(v) for k, v in data.items()}
        print("Lower keys and string values:")
        print(data)
        if 'cpf' in data.keys() and 'name' in data.keys():
            print("Found CPF in data.keys()")
            data = {k:v for (k,v) in data.items() if k in NaturalPerson.csv_editable()}
            print("Filtered keys for csv editable")
            print(data)
            new_person = NaturalPerson(**data)
            if cpf_isvalid(new_person.cpf):
                new_person.name = new_person.name.upper()
                new_person.user_id = current_user.id
                new_person.last_editor = current_user.id
                new_person.timestamp = datetime.utcnow()
                new_person.last_edit_time = datetime.utcnow()
                db.session.add(new_person)
                added += 1
            else: print('{} is not a valid CPF'.format(new_person.cpf))
        if 'cnpj' in data.keys() and 'name' in data.keys():
            data = {k:v for (k,v) in data.items() if k in LegalPerson.csv_editable()}
            new_person = LegalPerson(**data)
            if cnpj_isvalid(new_person.cnpj):
                new_person.name = new_person.name.upper()
                new_person.user_id = current_user.id
                new_person.last_editor = current_user.id
                new_person.timestamp = datetime.utcnow()
                new_person.last_edit_time = datetime.utcnow()
                db.session.add(new_person)
                added += 1
            else: print('{} is not a valid CNPJ'.format(new_person.cnpj))
    return added
