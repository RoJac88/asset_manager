from flask import render_template, current_app, flash, redirect, url_for
from app import db
from flask_login import current_user, login_required
from app.csv import bp
from app.csv.csv_parser import parse_csv
from app.csv.forms import NaturalPersonUploadForm, LegalPersonUploadForm
from app.models import NaturalPerson, LegalPerson, LegalPCodes
from werkzeug.utils import secure_filename

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload_csv', methods=['GET', 'POST'])
@login_required
def upload_csv():

    form1 = NaturalPersonUploadForm()
    form2 = LegalPersonUploadForm()

    codes = list(map(lambda x: x.code_digits, LegalPCodes.query.all()))
    code_ids = list(map(lambda x: x.id, LegalPCodes.query.all()))
    code_dict = dict(zip(codes, code_ids))

    if form1.validate_on_submit() and form1.submit1.data:
        filename = secure_filename(form1.csv.data.filename)
        target_directory = current_app.config.get('CSV_FOLDER')
        form1.csv.data.save(target_directory + filename)
        people = parse_csv(filename, current_user.id, NaturalPerson, code_dict=code_dict,
            data_offset=form1.data_offset.data,
            cpf_row=form1.cpf_row.data,
            name_row=form1.name_row.data,
            rg_row=form1.rg_row.data,
            email_row=form1.email_row.data)
        added = 0
        n_dups = 0
        for person in people:
            duplicates = NaturalPerson.query.filter_by(cpf=person.cpf).first()
            if duplicates == None:
                db.session.add(person)
                db.session.commit()
                added += 1
            else: n_dups += 1
        flash('Added {} people to the database, discarded {} duplicates'.format(added, n_dups))
        return redirect(url_for('main.people'))

    if form2.validate_on_submit() and form2.submit2.data:
        filename = secure_filename(form2.csv.data.filename)
        target_directory = current_app.config.get('CSV_FOLDER')
        form2.csv.data.save(target_directory + filename)
        people = parse_csv(filename, current_user.id, LegalPerson,
            data_offset=form2.data_offset.data,
            cnpj_row=form2.cnpj_row.data,
            name_row=form2.name_row.data,
            code_row=form2.code_row.data,
            email_row=form2.email_row.data,
            code_dict=code_dict)
        added = 0
        n_dups = 0
        for person in people:
            duplicates = LegalPerson.query.filter_by(cnpj=person.cnpj).first()
            if duplicates == None:
                db.session.add(person)
                db.session.commit()
                added += 1
            else: n_dups += 1
        flash('Added {} persons to the database, discarded {} duplicates'.format(added, n_dups))
        return redirect(url_for('main.people'))
    return render_template('csv/upload_csv.html', form1=form1, form2=form2)
