from flask import render_template, flash, redirect, url_for, request, current_app
from app import db
from app.main.forms import AddLegalPersonFrom, AddNaturalPersonForm, EditNaturalPersonForm, EditLegalPersonForm
from flask_login import current_user, login_required
from app.models import User, Person, NaturalPerson, LegalPerson
from datetime import datetime
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    n = len(Person.query.all())
    return render_template('index.html', n=n)

@bp.route('/add_person', methods=['GET', 'POST'])
@login_required
def add_person():
    form_natural = AddNaturalPersonForm()
    form_legal = AddLegalPersonFrom()
    if form_natural.validate_on_submit():
        user_id = current_user.id
        name = form_natural.name.data.upper()
        cpf = form_natural.cpf.data
        rg = form_natural.rg.data
        email = form_natural.email.data
        new_person = NaturalPerson(name=name,cpf=cpf,rg=rg,user_id=user_id,
            email=email,last_editor=user_id)
        db.session.add(new_person)
        db.session.commit()
        flash('Added {} to the database!'.format(name))
        return redirect(url_for('main.index'))
    if form_legal.validate_on_submit():
        user_id = current_user.id
        name = form_legal.name.data.upper()
        cnpj = form_legal.cnpj.data
        code = form_legal.code.data
        email = form_legal.email.data
        new_person = LegalPerson(name=name,cnpj=cnpj,code=code,user_id=user_id,
            email=email,last_editor=user_id)
        db.session.add(new_person)
        db.session.commit()
        flash('Added {} to the database!'.format(name))
        return redirect(url_for('main.index'))
    return render_template('add_person.html', form=(form_natural, form_legal))

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
    print(current_person.type)
    forms = {'legal': EditLegalPersonForm(), 'natural': EditNaturalPersonForm()}
    form = forms[current_person.type]
    if current_user.is_authenticated and current_person.type == 'natural':
        if form.validate_on_submit():
            current_person.name = form.name.data.upper()
            current_person.rg = form.rg.data
            current_person.email = form.email.data
            current_person.last_editor = current_user.id
            current_person.last_edit_time = datetime.utcnow()
            db.session.commit()
            flash('Your changes have been saved')
            return redirect(url_for('main.people'))
        elif current_person.type == 'legal':
            if form.validate_on_submit():
                current_person.name = form.name.data.upper()
                current_person.code = form.code.data
                current_person.email = form.email.data
                current_person.last_editor = current_user.id
                current_person.last_edit_time = datetime.utcnow()
                db.session.commit()
                flash('Your changes have been saved')
                return redirect(url_for('main.people'))
        elif request.method == 'GET':
            form.name.data = current_person.name
            form.rg.data = current_person.rg
            form.email.data = current_person.email
        return render_template('person_edit.html', person=current_person, form=form, User=User)
    else:
        return render_template('person_view.html', person=current_person, User=User)

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
