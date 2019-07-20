import os

from flask import render_template, redirect, url_for, request, current_app, jsonify, send_from_directory
from app import db
from flask_login import current_user, login_required
from app.models import User, Person, Cep
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    n = len(Person.query.all())
    return render_template('index.html', n=n)

@bp.route('/download/<filepath>', methods=['GET'])
@login_required
def download_file(filepath):
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    return send_from_directory(directory, filename, as_attachment=True)
