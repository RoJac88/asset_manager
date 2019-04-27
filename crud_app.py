import os
import csv
from app import create_app, db
from app.models import User, Person, NaturalPerson, LegalPerson, Lawsuit, LegalPCodes

app = create_app()

def populate_legal_codes():
    dir = os.path.join('app', 'main', 'static')
    source = os.path.join(dir, 'legal_codes.csv')
    with open(source, encoding='utf-8-sig', newline='') as csvfile:
        print('CSV file located')
        reader = csv.reader(csvfile)
        data = {}
        tups = []
        for row in reader:
            key, val = row[0].strip(), row[1].strip()
            data[key] = val
            tup = (key, key+' : '+val)
            tups.append(tup)
    for key, val in data.items():
        new_code = LegalPCodes(code_string=key, description=val)
        code_digits = key.replace('-','').strip()
        if code_digits.isdigit():
            new_code.code_digits = code_digits 
        if LegalPCodes.query.filter_by(code_digits=code_digits).first() == None:
            db.session.add(new_code)
            db.session.commit()
            print('Code added: {}'.format(key))
        else:
            print('Discarded duplicate code: {}'.format(key))

def clear_legal_codes():
    codes = LegalPCodes.query.all()
    if codes != None:
        for code in codes:
            db.session.delete(code)
        db.session.commit()
        print('legal_codes table clear')
    else:
        print('legal_codes table is already empty')

def print_codes():
    codes = LegalPCodes.query.all()
    if codes != []:
        for code in codes:
            print(code)
    else:
        print('legal_codes table is already empty')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Person': Person, 'NaturalPerson': NaturalPerson,
        'LegalPerson': LegalPerson, 'Lawsuit': Lawsuit, 'LegalPCodes': LegalPCodes,
        'populate_legal_codes' : populate_legal_codes, 'clear_legal_codes' : clear_legal_codes,
        'print_codes' : print_codes}