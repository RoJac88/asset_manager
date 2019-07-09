from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms import StringField, SubmitField, BooleanField, DateField
from wtforms.validators import ValidationError, DataRequired, Optional, Email
from app.models import NaturalPerson, LegalPCodes, Cep
from flask_wtf.file import FileField, FileRequired, FileAllowed

class UploadCSVForm(FlaskForm):
    csv = FileField('CSV (utf-8): ', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV flies only')
    ])
    bom = BooleanField('BOM mark: ')
    submit = SubmitField('Upload')

class EditNaturalPersonForm(FlaskForm):
    name = StringField('Name')
    rg = StringField('RG', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    addr_cep_nat = StringField('CEP')
    addr_city = StringField('City', validators=[Optional()])
    addr_uf = StringField('UF', validators=[Optional()])
    addr_bairro = StringField('Bairro', validators=[Optional()])
    addr_rua = StringField('Rua', validators=[Optional()])
    addr_num = StringField('N.', validators=[Optional()])
    addr_compl = StringField('Compl', validators=[Optional()])
    submit = SubmitField('Update')

    def validate_rg(self, rg):
        if len(rg.data) > 11: raise ValidationError('Invalid RG')

    def validate_addr_cep_nat(self, addr_cep):
        if Cep.query.get(addr_cep.data) == None:
            raise ValidationError('Invalid CEP')

class EditLegalPersonForm(FlaskForm):
    legal_name = StringField('Legal Name')
    code = QuerySelectField('Code',
        query_factory=lambda: LegalPCodes.query, allow_blank=False)
    email = StringField('Email', validators=[Optional(), Email()])
    addr_cep_leg = StringField('CEP')
    addr_city = StringField('City', validators=[Optional()])
    addr_uf = StringField('UF', validators=[Optional()])
    addr_bairro = StringField('Bairro', validators=[Optional()])
    addr_rua = StringField('Rua', validators=[Optional()])
    addr_num = StringField('N.', validators=[Optional()])
    addr_compl = StringField('Compl', validators=[Optional()])
    legal_birth = DateField(validators=[Optional()])
    legal_death = DateField(validators=[Optional()])
    legal_status = StringField(validators=[Optional()])
    submit = SubmitField('Update')

    def validate_cnpj(self, cnpj):
        if not cnpj.data.isdigit():
            raise ValidationError('CNPJ must contain only digits')
        if len(cnpj.data) != 14:
            raise ValidationError('Invalid CNPJ number')

    def validate_addr_cep_leg(self, addr_cep):
        if Cep.query.get(addr_cep.data) == None:
            raise ValidationError('Invalid CEP')

class AddLegalPersonFrom(FlaskForm):
    legal_name = StringField('Legal Name', validators=[DataRequired()])
    cnpj = StringField('CNPJ', validators=[DataRequired()])
    code = QuerySelectField('Code',
        query_factory=lambda: LegalPCodes.query, allow_blank=False)
    email = StringField('Email', validators=[Optional(), Email()])
    addr_cep_leg = StringField('CEP')
    addr_city = StringField('City', validators=[Optional()])
    addr_uf = StringField('UF', validators=[Optional()])
    addr_bairro = StringField('Bairro', validators=[Optional()])
    addr_rua = StringField('Rua', validators=[Optional()])
    addr_num = StringField('N.', validators=[Optional()])
    addr_compl = StringField('Compl', validators=[Optional()])
    legal_birth = DateField('YYY-MM-DD', validators=[Optional()])
    legal_death = DateField('YYY-MM-DD', validators=[Optional()])
    legal_status = StringField(validators=[Optional()])
    submit = SubmitField('Insert')

    def validate_cnpj(self, cnpj):
        if not cnpj.data.isdigit():
            raise ValidationError('CNPJ must contain only digits')
        if len(cnpj.data) != 14:
            raise ValidationError('Invalid CNPJ number')

    def validate_addr_cep_leg(self, addr_cep):
        if Cep.query.get(addr_cep.data) == None:
            raise ValidationError('Invalid CEP')

class AddNaturalPersonForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    cpf = StringField('CPF', validators=[DataRequired()])
    rg = StringField('RG', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    addr_cep_nat = StringField('CEP')
    addr_city = StringField('City', validators=[Optional()])
    addr_uf = StringField('UF', validators=[Optional()])
    addr_bairro = StringField('Bairro', validators=[Optional()])
    addr_rua = StringField('Rua', validators=[Optional()])
    addr_num = StringField('N.', validators=[Optional()])
    addr_compl = StringField('Compl', validators=[Optional()])
    submit = SubmitField('Insert')

    def validate_addr_cep_nat(self, addr_cep):
        if Cep.query.get(addr_cep.data) == None:
            raise ValidationError('Invalid CEP')

    def validate_rg(self, rg):
        if len(rg.data) > 11: raise ValidationError('Invalid RG')

    def validate_cpf(self, cpf):
        if not cpf.data.isdigit():
            raise ValidationError('CPF must contain only digits')
        if len(cpf.data) != 11:
            raise ValidationError('Invalid CPF number')
        person = NaturalPerson.query.filter_by(cpf=cpf.data).first()
        if person is not None:
            raise ValidationError('This CPF is already in the database')
        numbers = [int(digit) for digit in cpf.data if digit.isdigit()]
        # Validação do primeiro dígito verificador:
        sum_of_products = sum(a*b for a, b in zip(numbers[0:9], range(10, 1, -1)))
        expected_digit = (sum_of_products * 10 % 11) % 10
        if numbers[9] != expected_digit:
            raise ValidationError('Invalid CPF number')
        # Validação do segundo dígito verificador:
        sum_of_products = sum(a*b for a, b in zip(numbers[0:10], range(11, 1, -1)))
        expected_digit = (sum_of_products * 10 % 11) % 10
        if numbers[10] != expected_digit:
            raise ValidationError('Invalid CPF number')
