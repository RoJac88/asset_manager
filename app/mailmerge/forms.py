from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Optional 
from flask_wtf.file import FileField, FileRequired, FileAllowed

class AddDocx(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[Optional()])
    file = FileField('docx: ', validators=[
        FileRequired(),
        FileAllowed(['docx'], 'docx flies only')
    ])
    submit = SubmitField('Upload')
