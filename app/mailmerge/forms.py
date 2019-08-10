from flask_wtf import FlaskForm
from flask import flash
from wtforms import StringField, SubmitField, SelectField, IntegerField, Form, FieldList, FormField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Optional
from flask_wtf.file import FileField, FileRequired, FileAllowed
from app.models import NaturalPerson, LegalPerson, MergeField


class AddDocx(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[Optional()])
    file = FileField('docx: ', validators=[
        FileRequired(),
        FileAllowed(['docx'], 'docx flies only')
    ])
    submit = SubmitField('Upload')

class MergeFieldForm(Form):
    index = IntegerField('ID')
    field_id = IntegerField('db_id')
    target_class = SelectField('Entry', choices=[('NaturalPerson', 'NaturalPerson'), ('LegalPerson', 'LegalPerson'), ('Imovel', 'Imovel')])
    target_attr = SelectField('Attribute', choices=[
        ('addr_cep', 'addr_cep'), ('addr_rua', 'addr_rua'), ('addr_uf', 'addr_uf'),
        ('addr_num', 'addr_num'), ('addr_city', 'addr_city'), ('addr_compl', 'addr_compl'),
        ('addr_bairro', 'addr_bairro'), ('name', 'name'), ('legal_name', 'legal_name'),
        ('cpf', 'cpf'), ('cnpj', 'cnpj'), ('code', 'code'), ('rg', 'rg'),
        ('legal_birth', 'legal_birth'), ('legal_death', 'legal_death'), ('legal_status', 'legal_status'),
        ('email', 'email'), ])

class EditFieldsForm(FlaskForm):
    merge_fields = FieldList(FormField(MergeFieldForm), min_entries=1)
    submit = SubmitField('Update')

    def validate_merge_fields(self, merge_fields):
        item_list = []
        id_class = {}
        field_ids = []
        for item in merge_fields:
            if item.data['field_id'] in field_ids:
                error = 'Do not modify the field_id parameter!'
                flash(error, 'danger')
                raise ValidationError(error)
            if not MergeField.query.get(item.data['field_id']):
                error = 'No such field'
                flash(error, 'danger')
                raise ValidationError(error)
            field_ids.append(item.data['field_id'])
            if item.data['index'] not in id_class:
                id_class[item.data['index']] = item.data['target_class']
            else:
                if id_class[item.data['index']] != item.data['target_class']:
                    error = 'Only one target_class per ID allowed'
                    flash(error, 'danger')
                    raise ValidationError(error)
            my_data = (item.data['index'], item.data['target_class'], item.data['target_attr'])
            if my_data in item_list:
                error = 'Cannot set identical fields'
                flash(error, 'danger')
                raise ValidationError(error)
            item_list.append(my_data)
