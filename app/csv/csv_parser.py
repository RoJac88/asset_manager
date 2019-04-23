import csv
import os
import re
from flask import current_app

def get_email(email):
    email_regex = re.compile(r'^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$')
    mo = email_regex.search(email)
    if mo == None:
        return False
    else:
        return mo.group()

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

def parse_csv(filename, user_id, Person, data_offset=0, cpf_row=0, name_row=0, rg_row=0, email_row=0):
    target_directory = current_app.config.get('CSV_FOLDER')
    people = []
    with open(target_directory+filename, encoding='utf8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for line, row in enumerate(reader):
            if (line >= data_offset):
                new_person = Person(user_id=user_id, last_editor=user_id)
                cpf = row[cpf_row].replace('-','').replace('.','')
                if cpf_isvalid(cpf):
                    new_person.cpf = cpf
                try:
                    name = row[name_row].upper()
                except IndexError as error:
                    print(error)
                if name != None:
                    new_person.name = name
                if rg_row != None:
                    try:
                        rg = row[rg_row].replace('-','').replace('.','')
                    except IndexError as error:
                        print(error)
                    if len(rg)<11:
                        new_person.rg = rg
                if email_row != None:
                    try:
                        email = row[email_row]
                        _email = get_email(email)
                        if _email: new_person.email = _email
                    except IndexError as error:
                        print(error)
                if new_person.cpf and new_person.name:
                    people.append(new_person)
    os.remove(target_directory+filename)
    return people
