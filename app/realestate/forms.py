from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField, DateField, BooleanField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Optional, Email
from app.models import Cep, Imovel
from flask_wtf.file import FileField, FileRequired, FileAllowed

class OwnImovelForm(FlaskForm):
    owner = StringField('CPF / CNPJ', render_kw={'maxlength': 14, 'class': 'owner_id'})
    share = IntegerField('Shares', render_kw={'maxlength': 8, 'class': 'owner_quota', 'style':'max-width:64px'})

class UploadCSVForm(FlaskForm):
    csv = FileField('CSV (utf-8): ', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV flies only')
    ])
    bom = BooleanField('BOM mark: ')
    submit = SubmitField('Upload')

class ImovelForm(FlaskForm):
    name = StringField('Name')
    sql = StringField('SQL', render_kw={'maxlength': 9})
    addr_cep = StringField('CEP', render_kw={'maxlength': 8})
    addr_cidade = StringField('Cidade')
    addr_uf = StringField('UF', render_kw={'maxlength': 2})
    addr_bairro = StringField('Bairro')
    addr_rua = StringField('Rua')
    addr_num = StringField('N.')
    addr_compl = StringField('Compl')
    matricula_n = StringField('Matrícula')
    matricula_file = FileField('Matrícula (PDF): ', validators=[
        Optional(),
        FileAllowed(['pdf'], 'PDF flies only')
    ])
    owners = FieldList(FormField(OwnImovelForm), min_entries=1)
    shares = IntegerField('Total Shares', validators=[Optional()])
    submit = SubmitField('Insert')

    def validate_addr_cep(self, addr_cep):
        if Cep.query.get(addr_cep.data) == None:
            raise ValidationError('Invalid CEP')
