import os
from mailmerge import MailMerge

def get_person_data(person, fields):
    data = {}
    person_data = person.asdict()
    for field in fields:
        data[field.label] = person_data[field.label]
    return data

def create_docx(template_path, persons, fields, target):
    data = []
    document = MailMerge(template_path)
    for person in persons:
        doc_data = get_person_data(person, fields)
        data.append(doc_data)
    document.merge_pages(data)
    document.write(target)
    return len(data)
