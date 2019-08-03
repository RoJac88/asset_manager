import os
import csv

from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from app import db
from app.people.forms import AddLegalPersonFrom, AddNaturalPersonForm, EditNaturalPersonForm, EditLegalPersonForm, UploadCSVForm, EditContactForm
from flask_login import current_user, login_required
from app.models import User, Person, NaturalPerson, LegalPerson, PersonImovel, Imovel, LegalPCodes
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
    if form1.submit.data and form1.validate_on_submit():
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
    if form2.submit.data and form2.validate_on_submit():
        new_person = LegalPerson()
        new_person.user_id = current_user.id
        new_person.last_editor = current_user.id
        new_person.legal_name = form2.legal_name.data.upper()
        new_person.cnpj = form2.cnpj.data
        new_person.code = form2.code.data.id
        new_person.email = form2.email.data
        new_person.addr_cep = form2.addr_cep_leg.data
        new_person.addr_city = form2.addr_city.data
        new_person.addr_uf = form2.addr_uf.data
        new_person.addr_bairro = form2.addr_bairro.data
        new_person.addr_rua = form2.addr_rua.data
        new_person.addr_num = form2.addr_num.data
        new_person.addr_compl = form2.addr_compl.data
        if form2.legal_birth.data:
            new_person.legal_birth = form2.legal_birth.data
        if form2.legal_death.data:
            new_person.legal_death = form2.legal_death.data
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

@bp.route('/person', methods=['GET', 'POST'])
def person():
    person_id = request.args.get('person_id')
    if not person_id:
        return render_template('people/natural_person_view.html', person=None,
            form=None, assets=None, contact_form=None)
    current_person = Person.query.get(person_id)
    if not current_person:
        return render_template('people/natural_person_view.html', person=None,
            form=None, assets=None, contact_form=None)
    form = None
    contact_form = EditContactForm()
    print(contact_form.errors)
    template = 'people/natural_person_view.html'
    if current_person:
        forms = {'legal': EditLegalPersonForm(), 'natural': EditNaturalPersonForm()}
        templates = {'legal': 'people/legal_person_view.html', 'natural': 'people/natural_person_view.html'}
        form = forms[current_person.type]
        template = templates[current_person.type]
    _assets = PersonImovel.query.filter_by(person_id=current_person.id)
    assets = []
    for item in _assets:
        asset = Imovel.query.get(item.imovel_id)
        share = item.shares
        assets.append((asset, share))
    if contact_form.validate_on_submit():
        current_person.email = contact_form.email.data
        current_person.addr_cep = contact_form.addr_cep.data
        current_person.addr_city = contact_form.addr_city.data
        current_person.addr_uf = contact_form.addr_uf.data
        current_person.addr_bairro = contact_form.addr_bairro.data
        current_person.addr_rua = contact_form.addr_rua.data
        current_person.addr_num = contact_form.addr_num.data
        current_person.addr_compl = contact_form.addr_compl.data
        current_person.last_editor = current_user.id
        current_person.last_edit_time = datetime.utcnow()
        db.session.commit()
        flash('Contact details updated', 'success')
        return redirect(url_for('people.person', person_id=current_person.id))
    if form.validate_on_submit() and current_person.type == 'legal':
        current_person.legal_name = form.legal_name.data.upper()
        current_person.code = form.code.data.id
        if form.legal_birth.data:
            current_person.legal_birth = form.legal_birth.data
        if form.legal_death.data:
            current_person.legal_death = form.legal_death.data
        current_person.legal_status = form.legal_status.data
        current_person.last_editor = current_user.id
        current_person.last_edit_time = datetime.utcnow()
        db.session.commit()
        flash('Legal person details updated', 'success')
        return redirect(url_for('people.person', person_id=current_person.id))
    if form.validate_on_submit() and current_person.type == 'natural':
        current_person.name = form.name.data.upper()
        current_person.rg = form.rg.data
        current_person.last_editor = current_user.id
        current_person.last_edit_time = datetime.utcnow()
        db.session.commit()
        flash('Natural person details updated', 'success')
        return redirect(url_for('people.person', person_id=current_person.id))
    return render_template(template, person=current_person, form=form, assets=assets,
        contact_form=contact_form)

@bp.route('/person/delete', methods=['GET'])
@login_required
def delete_person():
    person_id = request.args.get('person_id')
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
