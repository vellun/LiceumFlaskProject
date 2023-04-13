from flask import Blueprint, redirect, render_template
from flask_login import login_user

from data.db_session import create_session
from data.login_form import LoginForm
from data.register_form import RegisterForm
from data.users_form import User

""" Модуль для авторизации и регистрации """

auth = Blueprint('auth', __name__, template_folder='templates', static_folder='static')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """ Функция авторизации """
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('auth/login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def reqister():
    """ Функция регистрации """
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', form=form, message="Пароли не совпадают")
        db_sess = create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form, message="Этот email уже используется")
        user = User(name=form.name.data, email=form.email.data,
                    surname=form.surname.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('./login')
    return render_template('auth/register.html', form=form)
