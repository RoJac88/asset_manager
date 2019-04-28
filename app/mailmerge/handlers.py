import os
from mailmerge import MailMerge

def get_person_data(person, fields):
    data = {}
    person_data = person.asdict()
    for field in fields:
        data[field.label] = person_data[field.label]
    return data

def create_docx(template, persons, fields):
    data = []
    for person in persons:
        doc_data = get_person_data(person, fields)
        data.append(doc_data)
    print(data)
