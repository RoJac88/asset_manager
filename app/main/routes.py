import os

from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from app import db
from flask_login import current_user, login_required
from app.models import User, Person, Cep
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    n = len(Person.query.all())
    return render_template('index.html', n=n)

@bp.route('/cep')
@login_required
def cep():
    cep_n = request.args.get('cep', '0')
    cep = Cep.query.get(str(cep_n))
    if cep:
        print(cep.asdict)
        return jsonify(cep.asdict())
    else:
        print('cep not found')
        return jsonify(error=404, text=str('404: CEP not found')), 404
