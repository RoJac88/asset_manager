from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import ValidationError, DataRequired, Optional, Email
from app.models import Cep, Imovel
from flask_wtf.file import FileField, FileRequired, FileAllowed

class ImovelForm(FlaskForm):
    name = StringField('Name')
    sql = StringField('SQL', render_kw={'maxlength': 9})
    addr_cep = StringField('CEP', render_kw={'maxlength': 8})
    addr_cidade = StringField('Cidade')
    addr_uf = StringField('UF', render_kw={'maxlength': 2, 'style' : 'width:40%;'})
    addr_bairro = StringField('Bairro')
    addr_rua = StringField('Rua')
    addr_num = StringField('N.', render_kw={'style' : 'width:20%;'})
    addr_compl = StringField('Compl')
    matricula_n = StringField('Matrícula')
    matricula_file = FileField('Matrícula (PDF): ', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'PDF flies only')
    ])
    submit = SubmitField('Insert')

    def validate_addr_cep(self, addr_cep):
        if Cep.query.get(addr_cep.data) == None:
            raise ValidationError('Invalid CEP')
