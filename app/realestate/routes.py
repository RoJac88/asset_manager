import os

from werkzeug.utils import secure_filename
from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from app import db
from app.realestate.forms import ImovelForm, UploadCSVForm, EditContactForm, EditOwnersForm, OwnImovelForm, MatriculaUpdateForm
from flask_login import current_user, login_required
from app.models import Imovel, Cep, PersonImovel, NaturalPerson, LegalPerson, Person
from datetime import datetime
from app.realestate import bp

def info_fields(im_dict):
    fields = []
    for key in im_dict.keys():
        _txt = key.split('-')
        if 'owner' in _txt and 'owners' in _txt:
            fields.append(_txt[1])
    if fields == []: return [0]
    else: return fields

@bp.route('/cep')
@login_required
def cep():
    cep_n = request.args.get('cep', '0')
    if len(str(cep_n)) != 8:
        return jsonify(error=404, text=str('404: CEP not found')), 404
    else:
        cep = Cep.query.get(str(cep_n))
        if cep:
            return jsonify(cep.asdict())
        else:
            return jsonify(error=404, text=str('404: CEP not found')), 404

@bp.route('/realestate', methods=['GET'])
def realestate():
    form = UploadCSVForm()
    imoveis = Imovel.query.all()
    return render_template('realestate/realestate.html', imoveis=imoveis, form=form)

@bp.route('/imovel', methods=['GET', 'POST'])
def imovel():
    imovel_id = request.args.get('imovel_id')
    imovel = Imovel.query.get(imovel_id)
    contact_form = EditContactForm()
    owners_form = EditOwnersForm()
    mat_form = MatriculaUpdateForm()
    info_fields = []
    owners = [] # List of tupples (PersonOjb, shares)
    ownerships = PersonImovel.query.filter_by(imovel_id=imovel_id)
    known_shares = 0
    if current_user.is_authenticated and owners_form.submit_owners.data and owners_form.validate_on_submit():
        imovel.total_shares = owners_form.total_shares.data
        for ownership in ownerships:
            db.session.delete(ownership)
        for data in owners_form.owners.data:
            print(data)
            n = data['owner']
            if n:
                if len(n) == 11:
                    owner = NaturalPerson.query.filter_by(cpf=n).first()
                if len(n) == 14:
                    owner = LegalPerson.query.filter_by(cnpj=n).first()
                share = data['share']
                if share: known_shares += share
                person_has_estate = PersonImovel(person=owner, estate=imovel, shares=share)
                db.session.add(person_has_estate)
        imovel.last_edit_time = datetime.utcnow()
        imovel.last_editor = current_user.id
        db.session.commit()
        flash('Successfully updated owners', 'success')
        unknown_shares = imovel.total_shares - known_shares
        return redirect(url_for('realestate.imovel', imovel_id=imovel.id, owners=owners,
            unknown_shares=unknown_shares, contact_form=contact_form, owners_form=owners_form,
            fields=range(len(owners)), mat_form=mat_form))
    for index, item in enumerate(ownerships):
        line = OwnImovelForm()
        owner = Person.query.get(item.person_id)
        shares = item.shares
        known_shares += shares
        if index > 0: owners_form.owners.append_entry()
        owners.append((owner, shares))
    unknown_shares = imovel.total_shares - known_shares
    while len(list(owners_form.owners)) > len(owners):
        owners_form.owners.pop_entry()
    if current_user.is_authenticated and mat_form.submit_mat.data and mat_form.validate_on_submit():
        target = current_app.config['RE_FILES_FOLDER']
        file = mat_form.matricula_file.data
        file_name = secure_filename('MAT_'+imovel.matricula_n+'SQL_'+imovel.sql+'.pdf')
        file_path = os.path.abspath(os.path.join(target,file_name))
        if file is not None:
            if os.path.isfile(file_path):
                os.remove(file_path)
            file.save(file_path)
            print('File saved: {}'.format(file_name))
            imovel.matricula_file = file_path
        imovel.matricula_file_date = mat_form.matricula_file_date.data
        imovel.last_edit_time = datetime.utcnow()
        imovel.last_editor = current_user.id
        db.session.commit()
        flash('Matricula file updated', 'success')
        return redirect(url_for('realestate.imovel', imovel_id=imovel.id, owners=owners,
            unknown_shares=unknown_shares, contact_form=contact_form, owners_form=owners_form,
            fields=range(len(owners)), mat_form=mat_form))
    if current_user.is_authenticated and contact_form.validate_on_submit():
        imovel.addr_cep = contact_form.addr_cep.data
        imovel.addr_city = contact_form.addr_city.data
        imovel.addr_uf = contact_form.addr_uf.data
        imovel.addr_bairro = contact_form.addr_bairro.data
        imovel.addr_rua = contact_form.addr_rua.data
        imovel.addr_num = contact_form.addr_num.data
        imovel.addr_compl = contact_form.addr_compl.data
        imovel.last_edit_time = datetime.utcnow()
        imovel.last_editor = current_user.id
        db.session.commit()
        flash('Contact details updated', 'success')
        return redirect(url_for('realestate.imovel', imovel_id=imovel.id, owners=owners,
            unknown_shares=unknown_shares, contact_form=contact_form, owners_form=owners_form,
            fields=range(len(owners)), mat_form=mat_form))
    return render_template('realestate/imovel_view.html', imovel=imovel, owners=owners,
        unknown_shares=unknown_shares, contact_form=contact_form, owners_form=owners_form,
        fields=range(len(owners)), mat_form=mat_form)

@bp.route('/add_realestate', methods=['GET', 'POST'])
@login_required
def add_realestate():
    form = ImovelForm()
    fields = info_fields(request.form)
    target = current_app.config['RE_FILES_FOLDER']
    if form.validate_on_submit() and form.submit.data:
        if not os.path.exists(target): os.makedirs(target)
        new_realestate = Imovel()
        file = form.matricula_file.data
        if file is not None:
            file_name = secure_filename('MAT_'+form.matricula_n.data+'SQL_'+form.sql.data+'.pdf')
            file_path = os.path.abspath(os.path.join(target,file_name))
            file.save(file_path)
            print('File saved: {}'.format(file_name))
            new_realestate.matricula_file = file_path
        new_realestate.name = form.name.data
        new_realestate.sql = form.sql.data
        new_realestate.addr_cep = form.addr_cep.data
        new_realestate.addr_cidade = form.addr_cidade.data
        new_realestate.addr_uf = form.addr_uf.data
        new_realestate.addr_bairro = form.addr_bairro.data
        new_realestate.addr_rua = form.addr_rua.data
        new_realestate.addr_num = form.addr_num.data
        new_realestate.addr_compl = form.addr_compl.data
        new_realestate.matricula_n = form.matricula_n.data
        new_realestate.matricula_file_date = form.matricula_file_date.data
        new_realestate.total_shares = form.total_shares.data
        new_realestate.user_id = current_user.id
        new_realestate.last_editor = current_user.id
        db.session.add(new_realestate)
        for data in form.owners.data:
            n = data['owner']
            if len(n) == 11:
                owner = NaturalPerson.query.filter_by(cpf=n).first()
            if len(n) == 14:
                owner = LegalPerson.query.filter_by(cnpj=n).first()
            share = data['share']
            person_has_estate = PersonImovel(person=owner, estate=new_realestate, shares=share)
            db.session.add(person_has_estate)
        db.session.commit()
        flash('Added {} to the database!'.format(new_realestate.name), 'success')
        return redirect(url_for('realestate.realestate'))
    if form.errors: print(form.errors)
    return render_template('realestate/add_realestate.html', form=form, fields=fields)

@bp.route('/imovel/<imovel_id>/delete', methods=['GET'])
@login_required
def delete_imovel(imovel_id):
    imovel = Imovel.query.get(imovel_id)
    if not imovel:
        flash('Cannot delete non existent record', 'danger')
        return redirect(url_for('realestate.realestate'))
    else:
        if imovel.matricula_file and os.path.isfile(imovel.matricula_file):
            os.remove(imovel.matricula_file)
        ownerships = PersonImovel.query.filter_by(imovel_id=imovel.id).all()
        if ownerships:
            for own in ownerships:
                db.session.delete(own)
        db.session.delete(imovel)
        db.session.commit()
        flash('Record deleted: {}'.format(imovel), 'success')
        return redirect(url_for('realestate.realestate'))
