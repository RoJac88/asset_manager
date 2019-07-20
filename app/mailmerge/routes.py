import os
import uuid

from flask import render_template, flash, redirect, url_for, current_app
from app import db
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from app.models import TemplateDocx, MergeField, UserFile
from app.mailmerge.forms import AddDocx, SelectLegalFields, SelectNaturalFields
from app.mailmerge.handlers import create_docx
from datetime import datetime
from app.mailmerge import bp
from mailmerge import MailMerge

@bp.route('/mailmerge', methods=['GET'])
@login_required
def mailmerge():
    templates = TemplateDocx.query.all()
    return render_template('mailmerge/mailmerge.html', templates=templates)

@bp.route('/add_template', methods=['GET', 'POST'])
@login_required
def add_template():
    form = AddDocx()
    target = current_app.config['TEMPLATES_FOLDER']
    if not os.path.exists(target): os.makedirs(target)
    if form.validate_on_submit():
        file = form.file.data
        name = form.name.data
        file_name = secure_filename(current_user.username.lower()+'_'+uuid.uuid4().hex +'.docx')
        file_path = os.path.join(target,file_name)
        file.save(file_path)
        print('File saved: {}'.format(file_name))
        new_template = TemplateDocx(
            file_path = file_path,
            name = name,
            description = form.description.data,
            file_size = os.path.getsize(file_path),
            user_id = current_user.id,
            timestamp = datetime.utcnow(),
            latest_use = datetime.utcnow(),
            docs_generated = 0)
        db.session.add(new_template)
        db.session.commit()
        doc = MailMerge(file_path)
        fields = doc.get_merge_fields()
        for field in fields:
            new_f = MergeField(label=field.lower().strip(), template=new_template.id)
            db.session.add(new_f)
            db.session.commit()
            print('Added <{}> field for template: {}'.format(field,name))
        flash('Template {} added. Detected {} merge fields'.format(name, len(fields)), 'info')
        return redirect(url_for('mailmerge.mailmerge'))
    return render_template('mailmerge/add_docx.html', form=form)

@bp.route('/template/<template_id>', methods=['GET', 'POST'])
def template(template_id):
    current_template = TemplateDocx.query.get(template_id)
    fields = current_template.fields
    labels = list(map(lambda x: x.label, fields))
    form = False
    if 'cpf' in labels: form = SelectNaturalFields()
    if 'cnpj' in labels: form = SelectLegalFields()
    if form and form.validate_on_submit():
        directory = os.path.join(current_app.root_path, current_app.config['OUTPUT_FOLDER'], secure_filename(current_user.username.lower()))
        if not os.path.exists(directory): os.makedirs(directory)
        file_name = secure_filename(uuid.uuid4().hex +'.docx')
        path = os.path.join(directory, file_name)
        n = create_docx(current_template.file_path, form.persons.data, fields, os.path.abspath(path))
        if n > 0:
            file_label = secure_filename(form.output_name.data)
            new_file = UserFile(name = file_label,
                timestamp = datetime.utcnow(),
                user_id = current_user.id,
                file_size = os.path.getsize(path),
                file_path = path)
            current_template.docs_generated += n
            db.session.add(new_file)
            db.session.commit()
            flash('Merge successful!\nFile: {}'.format(file_label), 'success')
        return redirect(url_for('auth.profile'))
    return render_template('mailmerge/template_view.html', template=current_template, fields=fields, form=form)

@bp.route('/user_file/<file_id>/delete', methods=['GET'])
@login_required
def delete_userfile(file_id):
    file = UserFile.query.get(file_id)
    if not file:
        flash('File does not exist', 'warning')
        return redirect(url_for('auth.profile'))
    os.remove(file.file_path)
    print('File {} removed by {}'.format(file.file_path, current_user))
    db.session.delete(file)
    db.session.commit()
    flash('File deleted: {}'.format(file.name), 'success')
    return redirect(url_for('auth.profile'))
