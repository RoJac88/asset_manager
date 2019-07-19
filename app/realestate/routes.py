import os

from werkzeug.utils import secure_filename
from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from app import db
from app.realestate.forms import ImovelForm, UploadCSVForm
from flask_login import current_user, login_required
from app.models import Imovel, Cep
from datetime import datetime
from app.realestate import bp

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

@bp.route('/imovel/<imovel_id>', methods=['GET'])
def imovel(imovel_id):
    imovel = Imovel.query.get(imovel_id)
    return render_template('realestate/imovel_view.html', imovel=imovel)

@bp.route('/add_realestate', methods=['GET', 'POST'])
@login_required
def add_realestate():
    form = ImovelForm()
    target = current_app.config['RE_FILES_FOLDER']
    if form.validate_on_submit() and form.submit.data:
        if not os.path.exists(target): os.makedirs(target)
        new_realestate = Imovel()
        file = form.matricula_file.data
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
        new_realestate.matricula_file_date = datetime.utcnow()
        db.session.add(new_realestate)
        db.session.commit()
        flash('Added {} to the database!'.format(new_realestate.name))
        return redirect(url_for('realestate.realestate'))
    return render_template('realestate/add_realestate.html', form=form)

@bp.route('/imovel/<imovel_id>/delete', methods=['GET'])
@login_required
def delete_imovel(imovel_id):
    imovel = Imovel.query.get(imovel_id)
    if not imovel:
        flash('Cannot delete non existent record')
        return redirect(url_for('realestate.realestate'))
    if os.path.isfile(imovel.matricula_file):
        os.remove(imovel.matricula_file)
    db.session.delete(imovel)
    db.session.commit()
    flash('Record deleted: {}'.format(imovel))
    return redirect(url_for('realestate.realestate'))
