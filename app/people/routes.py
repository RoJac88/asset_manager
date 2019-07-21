import os
import csv

from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from app import db
from app.people.forms import AddLegalPersonFrom, AddNaturalPersonForm, EditNaturalPersonForm, EditLegalPersonForm, UploadCSVForm
from flask_login import current_user, login_required
from app.models import User, Person, NaturalPerson, LegalPerson, PersonImovel
from app.people.helpers import import_csv
from datetime import datetime
from app.people import bp

@bp.route('/_get_person')
@login_required
def _get_person():
    _n = str(request.args.get('id', '0'))
    if len(_n) == 11:
        person = NaturalPerson.query.filter_by(cpf=_n).first()
        if person:
            return jsonify(person.asdict())
        else:
            return jsonify(error=404, text=str('404: CPF not found')), 404
    elif len(_n) == 14:
        person = LegalPerson.query.filter_by(cnpj=_n).first()
        if person:
            return jsonify(person.asdict())
        else:
            return jsonify(error=404, text=str('404: CNPJ not found')), 404
    else:
        return jsonify(error=404, text=str('404: entry not found')), 404

@bp.route('/add_person', methods=['GET', 'POST'])
@login_required
def add_person():
    form1 = AddNaturalPersonForm()
    form2 = AddLegalPersonFrom()
    if form1.validate_on_submit() and form1.submit.data:
        new_person = NaturalPerson()
        new_person.user_id = current_user.id
        new_person.last_editor = current_user.id
        new_person.name = form1.name.data.upper()
        new_person.cpf = form1.cpf.data
        new_person.rg = form1.rg.data
        new_person.email = form1.email.data
        new_person.addr_cep = form1.addr_cep_nat.data
        new_person.addr_city = form1.addr_city.data
        new_person.addr_uf = form1.addr_uf.data
        new_person.addr_bairro = form1.addr_bairro.data
        new_person.addr_rua = form1.addr_rua.data
        new_person.addr_num = form1.addr_num.data
        new_person.addr_compl = form1.addr_compl.data
        db.session.add(new_person)
        db.session.commit()
        flash('Added {} to the database!'.format(new_person.name), 'success')
        return redirect(url_for('main.index'))
    if form2.validate_on_submit() and form2.submit.data:
        new_person = LegalPerson()
        new_person.user_id = current_user.id
        new_person.last_editor = current_user.id
        new_person.legal_name = form2.legal_name.data.upper()
        new_person.cnpj = form2.cnpj.data
        new_person.code = form2.code.data.id
        new_person.email = form2.email.data
        new_person.addr_cep = form2.addr_cep_nat.data
        new_person.addr_city = form2.addr_city.data
        new_person.addr_uf = form2.addr_uf.data
        new_person.addr_bairro = form2.addr_bairro.data
        new_person.addr_rua = form2.addr_rua.data
        new_person.addr_num = form2.addr_num.data
        new_person.addr_compl = form2.addr_compl.data
        db.session.add(new_person)
        db.session.commit()
        flash('Added {} to the database!'.format(new_person.legal_name), 'info')
        return redirect(url_for('main.index'))
    return render_template('people/add_person.html', form1=form1, form2=form2)

@bp.route('/people', methods=['GET', 'POST'])
def people():
    form = UploadCSVForm()
    people = Person.query.all()
    if form.validate_on_submit():
        f = request.files['csv']
        added = import_csv(f, form.bom.data)
        db.session.commit()
        flash('Added {} entries to the database'.format(added), 'info')
        return redirect(url_for('people.people'))
    print(form.errors)
    return render_template('people/people.html', people=people, form=form)

@bp.route('/person/<person_id>', methods=['GET', 'POST'])
def person(person_id):
    current_person = Person.query.get(person_id)
    if current_person == None:
        return render_template('people/natural_person_view.html', person=current_person)
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
        current_person.addr_cep = form.addr_cep_nat.data
        current_person.addr_bairro = form.addr_bairro.data
        current_person.addr_rua = form.addr_rua.data
        current_person.addr_num = form.addr_num.data
        current_person.addr_uf = form.addr_uf.data
        current_person.addr_city = form.addr_city.data
        current_person.last_editor = current_user.id
        current_person.last_edit_time = datetime.utcnow()
        db.session.commit()
        flash('Your changes have been saved', 'success')
        return redirect(url_for('people.people'))
    elif form.validate_on_submit() and current_person.type == 'legal':
        current_person.legal_name = form.legal_name.data.upper()
        current_person.code = form.code.data.id
        current_person.email = form.email.data
        current_person.addr_cep = form.addr_cep_leg.data
        current_person.addr_bairro = form.addr_bairro.data
        current_person.addr_rua = form.addr_rua.data
        current_person.addr_num = form.addr_num.data
        current_person.addr_uf = form.addr_uf.data
        current_person.addr_city = form.addr_city.data
        current_person.legal_status = form.legal_status.data
        current_person.legal_birth = form.legal_birth.data
        current_person.legal_death = form.legal_death.data
        current_person.last_editor = current_user.id
        current_person.last_edit_time = datetime.utcnow()
        db.session.commit()
        flash('Your changes have been saved', 'success')
        return redirect(url_for('people.people'))
    elif request.method == 'GET' and current_person.type == 'natural':
        form.name.data = current_person.name
        form.rg.data = current_person.rg
        form.email.data = current_person.email
        form.addr_cep_nat.data = current_person.addr_cep
        form.addr_bairro.data = current_person.addr_bairro
        form.addr_rua.data = current_person.addr_rua
        form.addr_num.data = current_person.addr_num
        form.addr_uf.data = current_person.addr_uf
        form.addr_city.data = current_person.addr_city
        return render_template('people/natural_person_edit.html', person=current_person,
            form=form, creator=current_person.creator.username, editor=current_person.editor.username)
    elif current_person.type == 'legal':
        form.legal_name.data = current_person.legal_name
        form.code.data = current_person.category
        form.email.data = current_person.email
        form.addr_cep_leg.data = current_person.addr_cep
        form.addr_bairro.data = current_person.addr_bairro
        form.addr_rua.data = current_person.addr_rua
        form.addr_num.data = current_person.addr_num
        form.addr_uf.data = current_person.addr_uf
        form.addr_city.data = current_person.addr_city
        form.legal_status.data = current_person.legal_status
        form.legal_birth.data = current_person.legal_birth
        form.legal_death.data = current_person.legal_death
        return render_template('people/legal_person_edit.html', person=current_person,
            form=form, creator=current_person.creator.username, editor=current_person.editor.username)

@bp.route('/person/<person_id>/delete', methods=['GET'])
@login_required
def delete_person(person_id):
    person = Person.query.get(person_id)
    _p_repr = person.__repr__()
    if not person:
        flash('Cannot delete non existent record', 'danger')
        return redirect(url_for('people.people'))
    ownerships = PersonImovel.query.filter_by(person_id=person.id).all()
    if ownerships:
        for own in ownerships:
            db.session.delete(own)
    db.session.delete(person)
    db.session.commit()
    flash('Record deleted: {}'.format(_p_repr), 'success')
    return redirect(url_for('people.people'))
