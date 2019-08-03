from flask import flash
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms import StringField, SubmitField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Optional, Email
from app.models import NaturalPerson, LegalPCodes, Cep, LegalPerson
from app.people.helpers import cnpj_isvalid, cpf_isvalid
from flask_wtf.file import FileField, FileRequired, FileAllowed
from datetime import datetime

def validate_addr_cep(self, addr_cep):
    if Cep.query.get(addr_cep.data) == None:
        error = 'Invalid CEP'
        flash(error, 'danger')
        raise ValidationError('Invalid CEP')

def validate_rg(self, rg):
    if len(rg.data) > 11:
        error = 'Invalid RG'
        flash(error, 'danger')
        raise ValidationError(error)

def validate_cnpj(self, cnpj):
    if not cnpj_isvalid(cnpj.data):
        error = 'Invalid CNPJ'
        flash(error, 'danger')
        raise ValidationError(error)
    person = LegalPerson.query.filter_by(cnpj=cnpj.data).first()
    if person is not None:
        error = 'This CNPJ is already in the database'
        flash(error, 'danger')
        raise ValidationError(error)

def validate_cpf(self, cpf):
    if not cpf_isvalid(cpf.data):
        error = 'Invalid CPF number'
        flash(error, 'danger')
        raise ValidationError(error)
    person = NaturalPerson.query.filter_by(cpf=cpf.data).first()
    if person is not None:
        error = 'This CPF is already in the database'
        flash(error, 'danger')
        raise ValidationError(error)

class UploadCSVForm(FlaskForm):
    csv = FileField('CSV (utf-8): ', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV flies only')
    ])
    bom = BooleanField('BOM mark: ')
    submit = SubmitField('Upload')

class EditContactForm(FlaskForm):
    addr_cep = StringField('CEP', render_kw={'maxlength': 8}, validators=[validate_addr_cep])
    addr_city = StringField('City', validators=[Optional()])
    addr_uf = StringField('UF', validators=[Optional()], render_kw={'maxlength': 2})
    addr_bairro = StringField('Bairro', validators=[Optional()])
    addr_rua = StringField('Rua', validators=[Optional()])
    addr_num = StringField('N.', validators=[Optional()])
    addr_compl = StringField('Compl', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    submit = SubmitField('Update')

class EditNaturalPersonForm(FlaskForm):
    name = StringField('Name')
    rg = StringField('RG', validators=[Optional(), validate_rg])
    submit_details = SubmitField('Update')


class EditLegalPersonForm(FlaskForm):
    legal_name = StringField('Legal Name')
    code = QuerySelectField('Code',
        query_factory=lambda: LegalPCodes.query.all(), allow_blank=False)
    legal_birth = DateField(validators=[Optional()])
    legal_death = DateField(validators=[Optional()])
    legal_status = StringField(validators=[Optional()])
    submit_details = SubmitField('Update')


class AddLegalPersonFrom(FlaskForm):
    legal_name = StringField('Legal Name', validators=[DataRequired()])
    cnpj = StringField('CNPJ', validators=[DataRequired(), validate_cnpj], render_kw={'maxlength': 14})
    code = QuerySelectField('Code',
        query_factory=lambda: LegalPCodes.query, allow_blank=False)
    email = StringField('Email', validators=[Optional(), Email()])
    addr_cep_leg = StringField('CEP', render_kw={'maxlength': 8}, validators=[validate_addr_cep])
    addr_city = StringField('City', validators=[Optional()])
    addr_uf = StringField('UF', validators=[Optional()], render_kw={'maxlength': 2})
    addr_bairro = StringField('Bairro', validators=[Optional()])
    addr_rua = StringField('Rua', validators=[Optional()])
    addr_num = StringField('N.', validators=[Optional()])
    addr_compl = StringField('Compl', validators=[Optional()])
    legal_birth = DateField('Legal Birth', validators=[Optional()])
    legal_death = DateField('Legal Death', validators=[Optional()])
    legal_status = StringField(validators=[Optional()])
    submit = SubmitField('Insert')


class AddNaturalPersonForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    cpf = StringField('CPF', validators=[DataRequired(), validate_cpf], render_kw={'maxlength': 11})
    rg = StringField('RG', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    addr_cep_nat = StringField('CEP', render_kw={'maxlength': 8}, validators=[validate_addr_cep])
    addr_city = StringField('City', validators=[Optional()])
    addr_uf = StringField('UF', validators=[Optional()], render_kw={'maxlength': 2})
    addr_bairro = StringField('Bairro', validators=[Optional()])
    addr_rua = StringField('Rua', validators=[Optional()])
    addr_num = StringField('N.', validators=[Optional()])
    addr_compl = StringField('Compl', validators=[Optional()])
    submit = SubmitField('Insert')
