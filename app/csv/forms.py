from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.validators import ValidationError, Optional
from flask_wtf.file import FileField, FileRequired, FileAllowed

class NaturalPersonUploadForm(FlaskForm):
    csv = FileField('CSV (utf-8): ', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV flies only')
    ])
    data_offset = IntegerField('Data Offset')
    cpf_row = IntegerField('CPF row')
    name_row = IntegerField('Name row')
    rg_row = IntegerField('RG row', validators=[Optional()])
    email_row = IntegerField('Email row', validators=[Optional()])
    submit1 = SubmitField('Upload')

class LegalPersonUploadForm(FlaskForm):
    csv = FileField('CSV (utf-8): ', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV flies only')
    ])
    data_offset = IntegerField('Data Offset')
    cnpj_row = IntegerField('CNPJ row')
    name_row = IntegerField('Name row')
    code_row = IntegerField('Code row', validators=[Optional()])
    email_row = IntegerField('Email row', validators=[Optional()])
    submit2 = SubmitField('Upload')
