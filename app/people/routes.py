import os

from flask import render_template, flash, redirect, url_for, request, current_app
from app import db
from app.people.forms import AddLegalPersonFrom, AddNaturalPersonForm, EditNaturalPersonForm, EditLegalPersonForm
from flask_login import current_user, login_required
from app.models import User, Person, NaturalPerson, LegalPerson
from datetime import datetime
from app.people import bp

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
    return render_template('people/add_person.html', form1=form1, form2=form2)

@bp.route('/people')
def people():
    page = request.args.get('page', 1, type=int)
    people = Person.query.paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('main.people', page=people.next_num) if people.has_next else None
    prev_url = url_for('main.people', page=people.prev_num) if people.has_prev else None
    return render_template('people/people.html', people=people.items, next_url=next_url, prev_url=prev_url)

@bp.route('/person/<person_id>', methods=['GET', 'POST'])
def person(person_id):
    current_person = Person.query.get(person_id)
    if not current_user.is_authenticated and current_person.type == 'natural':
        return render_template('people/natural_person_view.html', person=current_person, creator=current_person.creator.username,
            editor=current_person.editor.username)
    if not current_user.is_authenticated and current_person.type == 'legal':
        return render_template('people/legal_person_view.html', person=current_person, creator=current_person.creator.username,
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
        return redirect(url_for('people.people'))
    elif form.validate_on_submit() and current_person.type == 'legal':
        current_person.name = form.name.data.upper()
        current_person.code = form.code.data.id
        current_person.email = form.email.data
        current_person.last_editor = current_user.id
        current_person.last_edit_time = datetime.utcnow()
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('people.people'))
    elif request.method == 'GET' and current_person.type == 'natural':
        form.name.data = current_person.name
        form.rg.data = current_person.rg
        form.email.data = current_person.email
        return render_template('people/natural_person_edit.html', person=current_person, form=form, creator=current_person.creator.username,
            editor=current_person.editor.username)
    elif current_person.type == 'legal':
        form.name.data = current_person.name
        form.code.data = current_person.category
        form.email.data = current_person.email
        return render_template('people/legal_person_edit.html', person=current_person, form=form, creator=current_person.creator.username,
            editor=current_person.editor.username)

@bp.route('/person/<person_id>/delete', methods=['GET'])
@login_required
def delete_person(person_id):
    person = Person.query.get(person_id)
    _p_repr = person.__repr__()
    if not person:
        flash('Cannot delete non existent record')
        return redirect(url_for('people.people'))
    db.session.delete(person)
    db.session.commit()
    flash('Record deleted: {}'.format(_p_repr))
    return redirect(url_for('people.people'))
