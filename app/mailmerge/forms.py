from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Optional
from flask_wtf.file import FileField, FileRequired, FileAllowed
from app.models import NaturalPerson, LegalPerson

class AddDocx(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[Optional()])
    file = FileField('docx: ', validators=[
        FileRequired(),
        FileAllowed(['docx'], 'docx flies only')
    ])
    submit = SubmitField('Upload')

class SelectNaturalFields(FlaskForm):
    persons = QuerySelectMultipleField('Persons',
        query_factory=lambda: NaturalPerson.query.all(), allow_blank=False)
    submit = SubmitField('Merge')

class SelectLegalFields(FlaskForm):
    persons = QuerySelectMultipleField('Persons',
        query_factory=lambda: LegalPerson.query.all(), allow_blank=False)
    submit = SubmitField('Merge')
