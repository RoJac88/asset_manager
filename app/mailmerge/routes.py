import os
import uuid
import json
from flask import render_template, flash, redirect, url_for, current_app, request, jsonify
from app import db
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from wtforms import SubmitField
from flask_login import current_user, login_required
from app.models import TemplateDocx, MergeField, UserFile, User, NaturalPerson, LegalPerson, Imovel
from app.mailmerge.forms import AddDocx, EditFieldsForm
from datetime import datetime
from app.mailmerge import bp
from mailmerge import MailMerge

@bp.route('/_get_entries')
@login_required
def _get_entries():
    choices = []
    target = str(request.args.get('target', '0'))
    targets = {'NaturalPerson': NaturalPerson, 'LegalPerson': LegalPerson, 'Imovel': Imovel}
    if target not in targets:
        return jsonify(error=404, text=str('404: entry not found')), 404
    attrs = targets[target].csv_editable()
    for attr in attrs:
        choices.append(attr)
    return jsonify(choices)

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

@bp.route('/template/delete', methods=['GET'])
@login_required
def delete_template():
    template_id = request.args.get('template_id')
    current_template = TemplateDocx.query.get(template_id)
    if not current_template:
        flash('Template does not exist', 'danger')
        return redirect(url_for('mailmerge.mailmerge'))
    fields = MergeField.query.filter_by(template=template_id)
    for field in fields:
        db.session.delete(field)
    name = current_template.name
    if os.path.isfile(current_template.file_path):
        os.remove(current_template.file_path)
        print('File deleted: {}'.format(current_template.file_path))
    db.session.delete(current_template)
    db.session.commit()
    flash('Template {} deleted'.format(name), 'success')
    return redirect(url_for('mailmerge.mailmerge'))


@bp.route('/template', methods=['GET', 'POST'])
@login_required
def template():
    template_id = request.args.get('template_id')
    if not template_id:
        return redirect(url_for('mailmerge.mailmerge'))
    current_template = TemplateDocx.query.get(template_id)
    if not current_template:
        flash('404 Error: Template not found', 'danger')
        return redirect(url_for('mailmerge.mailmerge'))
    fields = current_template.fields
    labels = list(map(lambda x: x.label, fields))
    avatars = current_app.config['AVATARS']
    author = User.query.get(current_template.user_id)
    if current_template.targets:
        targets = json.loads(current_template.targets)
    else: targets = {}
    fields_form = EditFieldsForm()
    class MergeForm(FlaskForm):
        pass
    if current_template.targets and len(targets) > 0:
        for index, target in enumerate(targets):
            formfield = QuerySelectField
            if index == 0: formfield = QuerySelectMultipleField
            if targets[target] == 'NaturalPerson':
                setattr(MergeForm, target,
                    formfield('Person-'+str(target), query_factory=lambda: NaturalPerson.query.all(), allow_blank=False))
            elif targets[target] == 'LegalPerson':
                setattr(MergeForm, target,
                    formfield('Legal Person-'+str(target), query_factory=lambda: LegalPerson.query.all(), allow_blank=False))
            elif targets[target] == 'Imovel':
                setattr(MergeForm, target,
                    formfield('Imovel-'+str(target), query_factory=lambda: Imovel.query.all(), allow_blank=False))
        MergeForm.submit_merge = SubmitField('Merge')
    merge_form = MergeForm()
    if merge_form.submit_merge.data and merge_form.validate_on_submit():
        names = []
        merge_data = []
        directory = os.path.join(current_app.config['OUTPUT_FOLDER'], current_user.username)
        output_basename = current_template.name+'-'
        if not os.path.isdir(directory):
            os.makedirs(directory)
        for entry in merge_form.data['0']:
            output_name = output_basename + entry.name
            my_data = {}
            for field in current_template.fields:
                if str(field.index) == '0':
                    my_data[field.label] = entry.asdict()[field.target_attr]
                else:
                    output_name += '-' + merge_form.data[str(field.index)].asdict()['name']
                    my_data[field.label] = merge_form.data[str(field.index)].asdict()[field.target_attr]
            names.append(output_name)
            merge_data.append(my_data)
        document_data = dict(zip(names, merge_data))
        for data in document_data:
            document = MailMerge(current_template.file_path)
            current_template.docs_generated += 1
            filename = data+'-'+str(current_template.docs_generated)+'.docx'
            print('Filename: {}'.format(filename))
            print('Data: {}'.format(document_data[data]))
            document.merge(**document_data[data])
            document.write(os.path.join(directory, secure_filename(filename)))
            new_file = UserFile()
            new_file.name = filename
            new_file.file_path = os.path.join(directory, secure_filename(filename))
            new_file.file_size = os.path.getsize(new_file.file_path)
            new_file.user_id = current_user.id
            db.session.add(new_file)
        current_template.latest_use = datetime.utcnow()
        db.session.commit()
        flash('Successfully generated {} files from template: {}'.format(len(document_data), current_template.name), 'success')
        return redirect(url_for('auth.profile'))
    if current_user == author and fields_form.submit.data and fields_form.validate_on_submit():
        targets = {}
        for data in fields_form.merge_fields.data:
            current_f = MergeField.query.get(data['field_id'])
            if not current_f:
                flash('Error: invalid field', 'danger')
                return redirect(url_for('mailmerge.template', template_id=template_id))
            if str(current_f.template) != str(template_id):
                flash('Insufficient permissions to edit this field', 'danger')
                return redirect(url_for('mailmerge.template', template_id=template_id))
            current_f.index = data['index']
            current_f.target_class = data['target_class']
            current_f.target_attr = data['target_attr']
            if data['index'] not in targets:
                targets[data['index']] = data['target_class']
        current_template.targets = json.dumps(targets)
        db.session.commit()
        flash('Your changes have been saved', 'success')
        return redirect(url_for('mailmerge.template', template_id=template_id))
    while len(fields) > len(fields_form.merge_fields):
        fields_form.merge_fields.append_entry()
    return render_template('mailmerge/template_view.html', template=current_template,
        fields=fields, fields_form=fields_form, author=author, avatars=avatars, n_fields=len(fields),
        targets=targets, merge_form=merge_form)

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
