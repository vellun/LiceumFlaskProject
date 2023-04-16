# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField, EmailField
from wtforms.validators import DataRequired


class AppForm(FlaskForm):
    fio = StringField('ФИО', validators=[DataRequired()])
    email = EmailField('Электронная почта', validators=[DataRequired()])
    tel = StringField("Номер телефона", validators=[DataRequired()])
    kolv = IntegerField('Количество человек', validators=[DataRequired()])
    comm = TextAreaField('Комментарий')
    submit = SubmitField('Отправить заявку')
