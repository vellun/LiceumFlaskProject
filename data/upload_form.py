from flask_wtf import FlaskForm
from wtforms import FileField
from wtforms import SubmitField


class UploadForm(FlaskForm):
    file = FileField()
    save = SubmitField('Сохранить')