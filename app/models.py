from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    persons = db.relationship('Person', backref='creator', lazy='dynamic', foreign_keys='Person.user_id')
    persons_edited = db.relationship('Person', backref='editor', lazy='dynamic', foreign_keys='Person.last_editor')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_edit_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    last_editor = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(12))
    lawsuits_plaintiff = db.relationship('Lawsuit', backref='active', lazy='dynamic', foreign_keys='Lawsuit.plaintiff')
    lawsuits_defendant = db.relationship('Lawsuit', backref='passive', lazy='dynamic', foreign_keys='Lawsuit.defendant')

    __mapper_args__ = {
        'polymorphic_identity':'person',
        'polymorphic_on':type
    }

class NaturalPerson(Person):
    id = db.Column(db.Integer, db.ForeignKey('person.id'), primary_key=True)
    cpf = db.Column(db.String(11), index=True, unique=True)
    rg = db.Column(db.String(11))

    def __repr__(self):
        return '<Natural Person {}, {}>'.format(self.cpf, self.name)

    __mapper_args__ = {
        'polymorphic_identity':'natural',
    }


class LegalPerson(Person):
    id = db.Column(db.Integer, db.ForeignKey('person.id'), primary_key=True)
    cnpj = db.Column(db.String(20), index=True, unique=True)
    code = db.Column(db.String(64))

    def __repr__(self):
        return '<Legal Person {}, {}>'.format(self.cnpj, self.name)

    __mapper_args__ = {
        'polymorphic_identity':'legal',
    }


class Lawsuit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), index=True, unique=True)
    plaintiff = db.Column(db.Integer, db.ForeignKey('person.id'))
    defendant = db.Column(db.Integer, db.ForeignKey('person.id'))
    val = db.Column(db.Integer, index=True) # valor da causa

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
