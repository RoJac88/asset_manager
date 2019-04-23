from flask import render_template, current_app, flash, redirect, url_for
from app import db
from flask_login import current_user, login_required
from app.csv import bp
from app.csv.csv_parser import parse_csv
from app.csv.forms import UploadForm
from app.models import Person
from werkzeug.utils import secure_filename

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload_csv', methods=['GET', 'POST'])
@login_required
def upload_csv():
    form = UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.csv.data.filename)
        target_directory = current_app.config.get('CSV_FOLDER')
        form.csv.data.save(target_directory + filename)
        people = parse_csv(filename, current_user.id, Person,
            data_offset=form.data_offset.data,
            cpf_row=form.cpf_row.data,
            name_row=form.name_row.data,
            rg_row=form.rg_row.data,
            email_row=form.email_row.data)
        added = 0
        n_dups = 0
        for person in people:
            duplicates = Person.query.filter_by(cpf=person.cpf).first()
            if duplicates == None:
                db.session.add(person)
                db.session.commit()
                added += 1
            else: n_dups += 1
        flash('Added {} people to the database, discarded {} duplicates'.format(added, n_dups))
        return redirect(url_for('main.people'))
    return render_template('csv/upload_csv.html', form=form)
