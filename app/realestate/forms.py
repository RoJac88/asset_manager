from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField, DateField, BooleanField, IntegerField, Form
from wtforms.validators import ValidationError, DataRequired, Optional, Email
from app.models import Cep, Imovel, Person, NaturalPerson, LegalPerson
from flask_wtf.file import FileField, FileRequired, FileAllowed

class OwnImovelForm(Form):
    owner = StringField('CPF / CNPJ', render_kw={'maxlength': 14, 'class': 'owner_id'})
    share = IntegerField('Shares', render_kw={'maxlength': 8, 'class': 'owner_share', 'style':'max-width:64px'})

class UploadCSVForm(FlaskForm):
    csv = FileField('CSV (utf-8): ', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV flies only')
    ])
    bom = BooleanField('BOM mark: ')
    submit = SubmitField('Upload')

class EditContactForm(FlaskForm):
    addr_cep = StringField('CEP', render_kw={'maxlength': 8})
    addr_city = StringField('City', validators=[Optional()])
    addr_uf = StringField('UF', validators=[Optional()], render_kw={'maxlength': 2})
    addr_bairro = StringField('Bairro', validators=[Optional()])
    addr_rua = StringField('Rua', validators=[Optional()])
    addr_num = StringField('N.', validators=[Optional()])
    addr_compl = StringField('Compl', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    submit = SubmitField('Update')

    def validate_addr_cep(self, addr_cep):
        if Cep.query.get(addr_cep.data) == None:
            raise ValidationError('Invalid CEP')

class EditOwnersForm(FlaskForm):
    owners = FieldList(FormField(OwnImovelForm), min_entries=1)
    total_shares = IntegerField('Total Shares')
    submit = SubmitField('Update')

class ImovelForm(FlaskForm):
    name = StringField('Name')
    sql = StringField('SQL', validators=[Optional()], render_kw={'maxlength': 9})
    addr_cep = StringField('CEP', render_kw={'maxlength': 8})
    addr_cidade = StringField('Cidade')
    addr_uf = StringField('UF', render_kw={'maxlength': 2})
    addr_bairro = StringField('Bairro', validators=[Optional()])
    addr_rua = StringField('Rua')
    addr_num = StringField('N.', validators=[Optional()])
    addr_compl = StringField('Compl', validators=[Optional()])
    matricula_n = StringField('Matrícula')
    matricula_file = FileField('Matrícula (PDF): ', validators=[
        Optional(),
        FileAllowed(['pdf'], 'PDF flies only')
    ])
    owners = FieldList(FormField(OwnImovelForm), min_entries=1)
    total_shares = IntegerField('Total Shares')
    submit = SubmitField('Insert')

    def validate_addr_cep(self, addr_cep):
        if Cep.query.get(addr_cep.data) == None:
            error = 'Invalid CEP'
            flash(error, 'danger')
            raise ValidationError(error)

    def validate_owners(self, owners):
        error = None
        owner_set = set()
        for item in owners:
            n = item.data['owner']
            share = item.data['share']
            if share is None or share == 0:
                error = 'Shares must be non zero'
                flash(error, 'danger')
                raise ValidationError(error)
            if n in owner_set:
                error = 'Only one line per owner'
                flash(error, 'danger')
                raise ValidationError(error)
            else:
                owner_set.add(n)
            if len(n)!=11 and len(n)!=14:
                error = 'Invalid length for CPF / CNPJ'
                flash(error, 'danger')
                raise ValidationError(error)
            if len(n)==11 and NaturalPerson.query.filter_by(cpf=n).first()==None:
                error = 'CPF not found'
                flash(error, 'danger')
                raise ValidationError(error)
            if len(n)==14 and LegalPerson.query.filter_by(cnpj=n).first()==None:
                error = 'CNPJ not found'
                flash(error, 'danger')
                raise ValidationError(error)
