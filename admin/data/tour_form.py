# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, IntegerField, TextAreaField, FileField
from wtforms.validators import DataRequired


class TourForm(FlaskForm):
    name = StringField('Название тура', validators=[DataRequired()])
    description = TextAreaField('Краткое описание', validators=[DataRequired()])
    start_date = DateField('Дата начала', validators=[DataRequired()])
    end_date = DateField('Дата окончания', validators=[DataRequired()])
    price = IntegerField('Стоимость', validators=[DataRequired()])
    file = FileField('Фотография места')
    full_description = TextAreaField('Подробное описание', validators=[DataRequired()])
    arrival = TextAreaField('Описание пути на место', validators=[DataRequired()])
    location = TextAreaField('Основная программа', validators=[DataRequired()])
    go_back = TextAreaField('Описание возвращения', validators=[DataRequired()])
    submit = SubmitField()
