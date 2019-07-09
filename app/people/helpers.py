import csv
import os
import io

from app import db
from flask_login import current_user
from app.models import NaturalPerson, LegalPerson, LegalPCodes, Cep
from itertools import chain
from datetime import datetime

def get_date(dt_string):
    try:
        date = datetime.strptime(dt_string, "%d-%m-%Y")
        return date
    except: ValueError
    try:
        date = datetime.strptime(dt_string, "%d/%m/%Y")
        return date
    except: ValueError
    try:
        date = datetime.strptime(dt_string, "%Y-%m-%d")
        return date
    except: ValueError
    try:
        date = datetime.strptime(dt_string, "%Y/%m/%d")
        return date
    except: ValueError
    return None


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

def cep_isvalid(cep):
    if Cep.query.get(cep) is None:
        return False
    else:
        return True

def safe_insert(dictionary, key, val):
    if not key in dictionary or dictionary[key] is None:
        dictionary[key] = val
        return True

def import_csv(fie_storage_obj, bom):
    code_digits = list(map(lambda x: x.code_digits, LegalPCodes.query.all()))
    code_ids = list(map(lambda x: x.id, LegalPCodes.query.all()))
    codes = dict(zip(code_digits, code_ids))
    encoding="utf8"
    if bom: encoding="utf_8_sig"
    print("Trying to import csv...")
    f = fie_storage_obj
    stream = io.StringIO(f.stream.read().decode(encoding), newline='')
    reader = csv.DictReader(stream)
    added = 0
    for row in reader:
        data = dict(row)
        data =  {k.lower().replace('-','').replace('/','').replace('.','').replace(' ','_'): str(v) for k, v in data.items()}
        if 'cpf' in data.keys() and 'name' in data.keys():
            data = {k:v for (k,v) in data.items() if k in NaturalPerson.csv_editable()}
            data['cpf'] = data['cpf'].replace('.','').replace('-','')
            if 'addr_cep' in data.keys():
                cep = str(data['addr_cep']).zfill(8)
                data['addr_cep'] = cep
                print(cep)
                if cep_isvalid(cep):
                    print('VALID!')
                    cep = Cep.query.get(cep)
                    safe_insert(data, 'addr_uf', cep.uf)
                    safe_insert(data, 'addr_city', cep.cidade)
                    safe_insert(data, 'addr_bairro', cep.bairro)
                    safe_insert(data, 'addr_rua', cep.rua)
                    safe_insert(data, 'addr_num', cep.num)
                    safe_insert(data, 'addr_compl', cep.compl)
                else:
                    print("Invalid CEP: {}".format(cep))
                    data['addr_cep'] = ""
            new_person = NaturalPerson(**data)
            cpfs = list(map(lambda x: x.cpf, NaturalPerson.query.all()))
            if new_person.cpf not in cpfs and cpf_isvalid(new_person.cpf):
                new_person.name = new_person.name.upper()
                new_person.user_id = current_user.id
                new_person.last_editor = current_user.id
                new_person.timestamp = datetime.utcnow()
                new_person.last_edit_time = datetime.utcnow()
                db.session.add(new_person)
                added += 1
            else: print('Validation failed for {}'.format(new_person))
        if 'cnpj' in data.keys() and 'legal_name' in data.keys():
            data = {k:v for (k,v) in data.items() if k in LegalPerson.csv_editable()}
            data['cnpj'] = data['cnpj'].replace('.','').replace('-','').replace('/','')
            if 'addr_cep' in data.keys():
                cep = str(data['addr_cep']).zfill(8)
                data['addr_cep'] = cep
                print(cep)
                if cep_isvalid(cep):
                    print('VALID!')
                    cep = Cep.query.get(cep)
                    safe_insert(data, 'addr_uf', cep.uf)
                    safe_insert(data, 'addr_city', cep.cidade)
                    safe_insert(data, 'addr_bairro', cep.bairro)
                    safe_insert(data, 'addr_rua', cep.rua)
                    safe_insert(data, 'addr_num', cep.num)
                    safe_insert(data, 'addr_compl', cep.compl)
                else:
                    print("Invalid CEP: {}".format(cep))
                    data['addr_cep'] = ""
            new_person = LegalPerson(**data)
            cnpjs = list(map(lambda x: x.cnpj, LegalPerson.query.all()))
            if new_person.cnpj not in cnpjs and cnpj_isvalid(new_person.cnpj):
                new_person.code = new_person.code.replace('-','')
                if new_person.code in code_digits:
                    new_person.code = codes[new_person.code]
                else:
                    print('found bad code')
                    new_person.code = 1
                new_person.legal_birth = get_date(new_person.legal_birth)
                new_person.legal_death = get_date(new_person.legal_death)
                new_person.legal_name = new_person.legal_name.upper()
                new_person.user_id = current_user.id
                new_person.last_editor = current_user.id
                new_person.timestamp = datetime.utcnow()
                new_person.last_edit_time = datetime.utcnow()
                db.session.add(new_person)
                added += 1
            else: print('Validation failed for {}'.format(new_person))
    return added
