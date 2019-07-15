import os
import csv
from app import create_app, db
from app.models import User, Person, NaturalPerson, LegalPerson, Lawsuit, LegalPCodes, TemplateDocx, MergeField, UserFile, Cep

app = create_app()

def populate_ceps():
    dir = os.path.join('app', 'realestate', 'data')
    source = os.path.join(dir, 'ceps.csv')
    with open(source, encoding='utf-8-sig', newline='') as csvfile:
        print('CSV file located')
        reader = csv.reader(csvfile)
        data = {}
        for row in reader:
            new_cep = Cep(
                id = str(row[0]).zfill(8),
                cidade = row[1],
                uf = row[2],
                bairro = row[3],
                rua = row[4],
                num = row[5],
                compl = row[6]
            )
            print('Adding new CEP: {}'.format(new_cep.id))
            db.session.add(new_cep)
            print('OK!')
    db.session.commit()
    print('CEPs imported')

def populate_legal_codes():
    dir = os.path.join('app', 'people', 'data')
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
    if codes != []:
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

def clear_mergemail():
    temps = TemplateDocx.query.all()
    if temps != []:
        for temp in temps:
            db.session.delete(temp)
        print('template_docx table clear')
    else:
        print('template_docx table is already empty')
    fields = MergeField.query.all()
    if fields != []:
        for field in fields:
            db.session.delete(field)
        print('merge_field table clear')
    else:
        print('merge_field table is already empty')
    files = UserFile.query.all()
    if files != []:
        for file in files:
            db.session.delete(file)
        print('user_files table clear')
    else:
        print('user_files table is already empty')
    db.session.commit()

def clear_files():
    files = UserFile.query.all()
    if files != []:
        for file in files:
            db.session.delete(file)
        print('user_files table clear')
    else:
        print('user_files table is already empty')
    db.session.commit()

def clear_persons():
    persons = Person.query.all()
    if persons != []:
        for person in persons:
            db.session.delete(person)
        print('persons table clear')
    else:
        print('persons table is already empty')
    db.session.commit()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Person': Person, 'NaturalPerson': NaturalPerson,
        'LegalPerson': LegalPerson, 'Lawsuit': Lawsuit, 'LegalPCodes': LegalPCodes,
        'TemplateDocx': TemplateDocx, 'MergeField': MergeField, 'cf': clear_files,
        'populate_legal_codes': populate_legal_codes, 'clear_legal_codes' : clear_legal_codes,
        'print_codes': print_codes, 'pop': populate_legal_codes, 'UserFile': UserFile, 'cm': clear_mergemail,
        'clear_persons' : clear_persons, 'ceps' : populate_ceps}
