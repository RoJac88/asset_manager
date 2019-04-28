import os
import uuid

from flask import render_template, flash, redirect, url_for, request, current_app
from app import db
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from app.models import TemplateDocx, MergeField
from app.mailmerge.forms import AddDocx, SelectLegalFields, SelectNaturalFields
from datetime import datetime
from app.mailmerge import bp
from mailmerge import MailMerge

@bp.route('/mailmerge', methods=['GET'])
@login_required
def mailmerge():
    page = request.args.get('page', 1, type=int)
    templates = TemplateDocx.query.paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('mailmerge.mailmerge', page=templates.next_num) if templates.has_next else None
    prev_url = url_for('mailmerge.mailmerge', page=templates.prev_num) if templates.has_prev else None
    return render_template('mailmerge/mailmerge.html', templates=templates.items, next_url=next_url, prev_url=prev_url)

@bp.route('/add_template', methods=['GET', 'POST'])
@login_required
def add_template():
    form = AddDocx()
    target = os.path.abspath(current_app.config['DOCX_FOLDER'])
    if not os.path.isdir(target):
        os.mkdir(target)
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
        flash('Template {} added. Detected {} merge fields'.format(name, len(fields)))
        return redirect(url_for('mailmerge.mailmerge'))
    return render_template('mailmerge/add_docx.html', form=form)

@bp.route('/template/<template_id>', methods=['GET'])
def template(template_id):
    current_template = TemplateDocx.query.get(template_id)
    fields = current_template.fields
    labels = list(map(lambda x: x.label, fields))
    form = False 
    if 'cpf' in labels: form = SelectNaturalFields()
    if 'cnpj' in labels: form = SelectLegalFields()
    return render_template('mailmerge/template_view.html', template=current_template, fields=fields, form=form)
