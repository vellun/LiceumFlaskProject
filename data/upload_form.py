from flask_wtf import FlaskForm
from wtforms import FileField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class UploadForm(FlaskForm):
    file = FileField(validators=[DataRequired()])
    save = SubmitField('Сохранить')