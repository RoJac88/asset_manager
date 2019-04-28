import os
import csv
import uuid

from flask import render_template, flash, redirect, url_for, request, current_app
from app import db
from werkzeug.utils import secure_filename
from app.main.forms import AddLegalPersonFrom, AddNaturalPersonForm, EditNaturalPersonForm, EditLegalPersonForm, AddDocx
from flask_login import current_user, login_required
from app.models import User, Person, NaturalPerson, LegalPerson, LegalPCodes, TemplateDocx, MergeField
from datetime import datetime
from app.main import bp
from mailmerge import MailMerge

@bp.route('/')
@bp.route('/index')
def index():
    n = len(Person.query.all())
    return render_template('index.html', n=n)

@bp.route('/add_person', methods=['GET', 'POST'])
@login_required
def add_person():
    form1 = AddNaturalPersonForm()
    form2 = AddLegalPersonFrom()
    if form1.validate_on_submit() and form1.submit.data:
        user_id = current_user.id
        name = form1.name.data.upper()
        cpf = form1.cpf.data
        rg = form1.rg.data
        email = form1.email.data
        new_person = NaturalPerson(name=name,cpf=cpf,rg=rg,user_id=user_id,
            email=email,last_editor=user_id)
        db.session.add(new_person)
        db.session.commit()
        flash('Added {} to the database!'.format(name))
        return redirect(url_for('main.index'))
    if form2.validate_on_submit() and form2.submit.data:
        user_id = current_user.id
        name = form2.name.data.upper()
        cnpj = form2.cnpj.data
        code = form2.code.data.id
        email = form2.email.data
        new_person = LegalPerson(name=name,cnpj=cnpj,code=code,user_id=user_id,
            email=email,last_editor=user_id)
        db.session.add(new_person)
        db.session.commit()
        flash('Added {} to the database!'.format(name))
        return redirect(url_for('main.index'))
    return render_template('add_person.html', form1=form1, form2=form2)

@bp.route('/people')
def people():
    page = request.args.get('page', 1, type=int)
    people = Person.query.paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('main.people', page=people.next_num) if people.has_next else None
    prev_url = url_for('main.people', page=people.prev_num) if people.has_prev else None
    return render_template('people.html', people=people.items, next_url=next_url, prev_url=prev_url)

@bp.route('/person/<person_id>', methods=['GET', 'POST'])
def person(person_id):
    current_person = Person.query.get(person_id)
    if not current_user.is_authenticated and current_person.type == 'natural':
        return render_template('natural_person_view.html', person=current_person, creator=current_person.creator.username,
            editor=current_person.editor.username)
    if not current_user.is_authenticated and current_person.type == 'legal':
        return render_template('legal_person_view.html', person=current_person, creator=current_person.creator.username,
            editor=current_person.editor.username)
    forms = {'legal': EditLegalPersonForm(), 'natural': EditNaturalPersonForm()}
    form = forms[current_person.type]
    if form.validate_on_submit() and current_person.type == 'natural':
        current_person.name = form.name.data.upper()
        current_person.rg = form.rg.data
        current_person.email = form.email.data
        current_person.last_editor = current_user
        current_person.last_edit_time = datetime.utcnow()
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('main.people'))
    elif form.validate_on_submit() and current_person.type == 'legal':
        current_person.name = form.name.data.upper()
        current_person.code = form.code.data.id
        current_person.email = form.email.data
        current_person.last_editor = current_user.id
        current_person.last_edit_time = datetime.utcnow()
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('main.people'))
    elif request.method == 'GET' and current_person.type == 'natural':
        form.name.data = current_person.name
        form.rg.data = current_person.rg
        form.email.data = current_person.email
        return render_template('natural_person_edit.html', person=current_person, form=form, creator=current_person.creator.username,
            editor=current_person.editor.username)
    elif current_person.type == 'legal':
        form.name.data = current_person.name
        form.code.data = current_person.category
        form.email.data = current_person.email
        return render_template('legal_person_edit.html', person=current_person, form=form, creator=current_person.creator.username,
            editor=current_person.editor.username)

@bp.route('/person/<person_id>/delete', methods=['GET'])
@login_required
def delete_person(person_id):
    person = Person.query.get(person_id)
    _p_repr = person.__repr__()
    if not person:
        flash('Cannot delete non existent record')
        return redirect(url_for('main.people'))
    db.session.delete(person)
    db.session.commit()
    flash('Record deleted: {}'.format(_p_repr))
    return redirect(url_for('main.people'))

@bp.route('/mailmerge', methods=['GET'])
@login_required
def mailmerge():
    page = request.args.get('page', 1, type=int)
    templates = TemplateDocx.query.paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('main.mailmerge', page=templates.next_num) if templates.has_next else None
    prev_url = url_for('main.mailmerge', page=templates.prev_num) if templates.has_prev else None
    return render_template('mailmerge.html', templates=templates.items, next_url=next_url, prev_url=prev_url)

@bp.route('/add_template', methods=['GET', 'POST'])
@login_required
def add_template():
    form = AddDocx()
    target = os.path.abspath(current_app.config['DOCX_FOLDER'])
    if not os.path.isdir(target):
        os.mkdir(target)
    if form.validate_on_submit():
        file = form.file.data
        name = form.name.data
        file_name = secure_filename(current_user.username.lower()+'_'+uuid.uuid4().hex +'.docx')
        file_path = os.path.join(target,file_name)
        file.save(file_path)
        print('File saved: {}'.format(file_name))
        new_template = TemplateDocx(
            file_path = file_path,
            name = name,
            description = form.description.data,
            file_size = os.path.getsize(file_path),
            user_id = current_user.id,
            timestamp = datetime.utcnow(),
            latest_use = datetime.utcnow(),
            docs_generated = 0)
        db.session.add(new_template)
        db.session.commit()
        doc = MailMerge(file_path)
        fields = doc.get_merge_fields()
        for field in fields:
            new_f = MergeField(label=field.lower().strip(), template=new_template.id)
            db.session.add(new_f)
            db.session.commit()
            print('Added <{}> field for template: {}'.format(field,name))
        flash('Template {} added. Detected {} merge fields'.format(name, len(fields)))
        return redirect(url_for('main.mailmerge'))
    return render_template('add_docx.html', form=form)

@bp.route('/template/<template_id>', methods=['GET'])
def template(template_id):
    current_template = TemplateDocx.query.get(template_id)
    fields = current_template.fields
    return render_template('template_view.html', template=current_template, fields=fields)
