from sqlalchemy.orm import backref
from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from app import db, login
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    avatar = db.Column(db.Integer, default=0)
    password_hash = db.Column(db.String(128))
    persons = db.relationship('Person', backref='creator', lazy='dynamic', foreign_keys='Person.user_id')
    files = db.relationship('UserFile', backref='owner', lazy='select', foreign_keys='UserFile.user_id')
    estates = db.relationship('Imovel', backref='creator', lazy='dynamic', foreign_keys='Imovel.user_id')
    persons_edited = db.relationship('Person', backref='editor', lazy='dynamic', foreign_keys='Person.last_editor')
    estates_edited = db.relationship('Imovel', backref='editor', lazy='dynamic', foreign_keys='Imovel.last_editor')
    templates_added = db.relationship('TemplateDocx', backref='author', lazy='dynamic', foreign_keys='TemplateDocx.user_id')

    def __repr__(self):
        return self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_path = db.Column(db.String(130))
    file_size = db.Column(db.Integer())
    type = db.Column(db.String(12))

    __mapper_args__ = {
        'polymorphic_identity':'file',
        'polymorphic_on':type
    }

class UserFile(File):
    id = db.Column(db.Integer, db.ForeignKey('file.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'user',
    }

class ImovelFile(File):
    id = db.Column(db.Integer, db.ForeignKey('file.id'), primary_key=True)
    imovel_id = db.Column(db.Integer, db.ForeignKey('imovel.id'))

    __mapper_args__ = {
        'polymorphic_identity':'im',
    }

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    addr_cep = db.Column(db.String(8), db.ForeignKey('cep.id'))
    addr_bairro = db.Column(db.String(64))
    addr_rua = db.Column(db.String(64))
    addr_num = db.Column(db.String(5))
    addr_city = db.Column(db.String(32))
    addr_uf = db.Column(db.String(2))
    addr_compl = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_edit_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    last_editor = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(12))
    lawsuits_plaintiff = db.relationship('Lawsuit', backref='active', lazy='dynamic', foreign_keys='Lawsuit.plaintiff')
    lawsuits_defendant = db.relationship('Lawsuit', backref='passive', lazy='dynamic', foreign_keys='Lawsuit.defendant')
    estate_ownership = association_proxy('person_imovel', 'imovel')

    __mapper_args__ = {
        'polymorphic_identity':'person',
        'polymorphic_on':type
    }

class PersonImovel(db.Model):
    __tablename__ = 'person_imovel'
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), primary_key=True)
    imovel_id = db.Column(db.Integer, db.ForeignKey('imovel.id'), primary_key=True)
    shares = db.Column(db.Integer)

    person = db.relationship(Person,
        backref=backref("estate_ownership", cascade="all, delete-orphan"))

    estate = db.relationship("Imovel")

    def __init__(self, person=None, estate=None, shares=None):
        self.person = person
        self.estate = estate
        self.shares = shares

class NaturalPerson(Person):
    id = db.Column(db.Integer, db.ForeignKey('person.id'), primary_key=True)
    name = db.Column(db.String(64))
    cpf = db.Column(db.String(11), index=True, unique=True)
    rg = db.Column(db.String(11))

    def __repr__(self):
        return '{}, CPF: {}'.format(self.name, self.cpf)

    __mapper_args__ = {
        'polymorphic_identity':'natural',
    }

    def asdict(self):
        return {
            'name' : self.name,
            'cpf' : self.cpf[:3]+'.'+self.cpf[3:6]+'.'+self.cpf[6:9]+'-'+self.cpf[9:],
            'sic' : self.cpf[:3]+'.'+self.cpf[3:6]+'.'+self.cpf[6:9]+'-'+self.cpf[9:],
            'rg' : str(self.rg),
            'email' : self.email,
            'addr_bairro': self.addr_bairro,
            'addr_rua': self.addr_rua,
            'addr_num': self.addr_num,
            'addr_cep': self.addr_cep,
            'addr_city': self.addr_city,
            'addr_uf': self.addr_uf,
            }

    @staticmethod
    def csv_editable():
        return {'name', 'cpf', 'rg', 'email', 'addr_bairro', 'addr_rua',
            'addr_num', 'addr_cep', 'addr_city', 'addr_uf',}

class LegalPerson(Person):
    id = db.Column(db.Integer, db.ForeignKey('person.id'), primary_key=True)
    legal_name = db.Column(db.String(64))
    cnpj = db.Column(db.String(20), index=True, unique=True)
    code = db.Column(db.Integer, db.ForeignKey('legal_codes.id'))
    legal_birth = db.Column(db.Date, index=True, default=date(1889,11,15))
    legal_death = db.Column(db.Date)
    legal_status = db.Column(db.String(22))

    def __repr__(self):
        return '{}, CNPJ: {}'.format(self.legal_name, self.cnpj)

    __mapper_args__ = {
        'polymorphic_identity':'legal',
    }

    @staticmethod
    def csv_editable():
        return {'legal_name', 'cnpj', 'code', 'email', 'addr_bairro', 'addr_rua', 'legal_status',
            'addr_num', 'addr_cep', 'addr_city', 'addr_uf', 'legal_birth', 'legal_death'}

    def asdict(self):
        mycode = LegalPCodes.query.get(self.code)
        return {
            'name': self.legal_name,
            'cnpj': self.cnpj[:2]+'.'+self.cnpj[2:5]+'.'+self.cnpj[5:8]+'/'+self.cnpj[8:12]+'-'+self.cnpj[12:],
            'sic': self.cnpj[:2]+'.'+self.cnpj[2:5]+'.'+self.cnpj[5:8]+'/'+self.cnpj[8:12]+'-'+self.cnpj[12:],
            'code': str(mycode),
            'email': self.email,
            'addr_bairro': self.addr_bairro,
            'addr_rua': self.addr_rua,
            'addr_num': self.addr_num,
            'addr_cep': self.addr_cep,
            'addr_city': self.addr_city,
            'addr_uf': self.addr_uf,
            'legal_birth': str(self.legal_birth),
            'legal_death': str(self.legal_death),
            'legal_status': self.legal_status,
            }


class LegalPCodes(db.Model):
    __tablename__ = 'legal_codes'
    id = db.Column(db.Integer, primary_key=True)
    code_digits = db.Column(db.String(5), index=True, unique=True)
    description = db.Column(db.String(64))
    code_string = db.Column(db.String(6))
    legal_persons = db.relationship('LegalPerson', backref='category', lazy='select', foreign_keys='LegalPerson.code')

    def __repr__(self):
        return '{} - {}'.format(self.code_string, self.description)

class TemplateDocx(db.Model):
    __tablename__ = 'template_docx'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(24))
    description = db.Column(db.String(128))
    file_path = db.Column(db.String(128))
    file_size = db.Column(db.Integer)
    fields = db.relationship('MergeField', backref='document', lazy='select', foreign_keys='MergeField.template')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    latest_use = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    docs_generated = db.Column(db.Integer)

class MergeField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(24))
    template = db.Column(db.Integer, db.ForeignKey('template_docx.id'))

class Imovel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(24))
    sql = db.Column(db.String(9), index=True)
    addr_cep = db.Column(db.String(8), db.ForeignKey('cep.id'))
    addr_cidade = db.Column(db.String(24))
    addr_uf = db.Column(db.String(2))
    addr_bairro = db.Column(db.String(24))
    addr_rua = db.Column(db.String(64))
    addr_num = db.Column(db.String(5))
    addr_compl = db.Column(db.String(64))
    matricula_n = db.Column(db.String(6))
    matricula_file = db.Column(db.String(128))
    matricula_file_date = db.Column(db.DateTime, index=True, default=datetime(1889,11,15))
    total_shares = db.Column(db.Integer)
    files = db.relationship('ImovelFile', backref='imovel', lazy='select', foreign_keys='ImovelFile.imovel_id')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    last_editor = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_edit_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class Cep(db.Model):
    id = db.Column(db.String(8), primary_key=True)
    cidade = db.Column(db.String(24))
    uf = db.Column(db.String(2))
    bairro = db.Column(db.String(48))
    rua = db.Column(db.String(64))
    num = db.Column(db.String(8))
    compl = db.Column(db.String(24))
    legal_persons = db.relationship('LegalPerson', backref='cep', lazy='select', foreign_keys='LegalPerson.addr_cep')
    imoveis = db.relationship('Imovel', backref='cep', lazy='select', foreign_keys='Imovel.addr_cep')

    def asdict(self):
        return {
            'cidade' : self.cidade,
            'uf' : self.uf,
            'bairro' : self.bairro,
            'rua' : self.rua,
            'num' : self.num,
            'compl' : self.compl,
            }

class Lawsuit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), index=True, unique=True)
    plaintiff = db.Column(db.Integer, db.ForeignKey('person.id'))
    defendant = db.Column(db.Integer, db.ForeignKey('person.id'))
    val = db.Column(db.Integer, index=True) # valor da causa
