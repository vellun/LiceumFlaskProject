import json

from flask import Blueprint, redirect, render_template, send_file
from flask_login import login_user, login_required
from requests import get

from data.db_session import create_session
from data.feedbacks_form import Feedback
from data.login_form import LoginForm
from data.tours_form import Tour
from data.users_form import User

""" Админ-панель(для работы используется api) """

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


@login_required
@admin.route('/')  # Главная страница админки
def main_page():
    db_sess = create_session()
    tours = db_sess.query(Tour).all()
    feedbacks = db_sess.query(Feedback).all()
    users = db_sess.query(User).all()
    return render_template("admin/main.html", tours=str(len(tours)), feedbacks=str(len(feedbacks)),
                           users=str(len(users)))


@admin.route('/tours_management')  # Управление турами(страница со всеми турами)
def tours_management():
    tours = get("http://localhost:5000/api/tours").json()  # Получение туров через api
    last_tour = None

    tours = [tours["tours"][i:i + 2] for i in
             range(0, len(tours["tours"]), 2)]  # Формируем туры по парам чтобы расположить на странице
    if tours and len(tours[-1]) % 2:  # Если в последнюю пару попал один тур, записываем его в отдельную переменную
        last_tour, tours = tours[-1], tours[:-1]
    return render_template("admin/tours_manage.html", tours=tours, last_tour=last_tour)


@admin.route('/download_tours')
def download_all_tours_json():  # Загрузка json-файла со всеми турами
    tours = get("http://localhost:5000/api/tours").json()  # Получение туров через api
    with open('admin/static/json/all_tours.json', 'w') as file:
        json.dump(tours, file, ensure_ascii=False)  # Запись в файл
    # Отправка файла
    return send_file('admin/static/json/all_tours.json', download_name='all_tours.json', as_attachment=True)


@admin.route('/download_tours/<tour_id>')
def download_one_tour_json(tour_id):  # Загрузка json-файла с одним туром
    tour = get(f"http://localhost:5000/api/tours/{tour_id}").json()  # Получение тура через api
    with open(f'admin/static/json/tour_{tour_id}.json', 'w') as file:
        json.dump(tour, file, ensure_ascii=False)  # Запись в файл
    # Отправка файла
    return send_file(f'admin/static/json/tour_{tour_id}.json', download_name=f'tour_{tour_id}.json', as_attachment=True)


@admin.route('/login', methods=['GET', 'POST'])
def login():
    """ Функция авторизации """
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if not user.is_admin:  # Если пользователь не явдяется админом
            return render_template('admin/login.html', message="Вы не обладаете правами администратора.", form=form)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("./")
        return render_template('admin/login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('admin/login.html', form=form)


@admin.errorhandler(401)  # Ошибка авторизации
def not_authenticated(_):
    return redirect("./login")
