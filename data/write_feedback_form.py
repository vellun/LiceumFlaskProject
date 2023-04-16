# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, NumberRange, InputRequired, Length


class WriteFeedbackForm(FlaskForm):
    score = IntegerField("Оцените полет от 1 до 5", default=5, validators=[DataRequired(), NumberRange(min=1, max=5)])
    pluses = TextAreaField('Опишите достоинства путешествия', validators=[DataRequired()])
    minuses = TextAreaField('Опишите недостатки путешествия', validators=[DataRequired()])
    comment = TextAreaField('Оставьте комментарий', validators=[DataRequired()])
    file = MultipleFileField('Прикрепите фотографии',
                             validators=[Length(max=10, message='Вы можете выбрать максимум 10 фото')])
    submit = SubmitField("Отправить")
