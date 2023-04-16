import datetime
import json

from flask import Blueprint, redirect, render_template, send_file, request, abort
from flask_login import login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from requests import get, post, delete
from wtforms import SubmitField

from .data.tour_form import TourForm
from data.db_session import create_session
from data.feedbacks_form import Feedback
from data.login_form import LoginForm
from data.tours_form import Tour
from data.users_form import User

""" Админ-панель(для работы используется api) """

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')
ADMIN = False


def change_admin(boolean: bool):
    global ADMIN
    ADMIN = boolean


@login_required
@admin.route('/')  # Главная страница админки
def main_page():
    if ADMIN:  # Если пользователь админ
        db_sess = create_session()
        tours = db_sess.query(Tour).all()
        feedbacks = db_sess.query(Feedback).all()
        users = db_sess.query(User).all()
        return render_template("admin/main.html", tours=str(len(tours)), feedbacks=str(len(feedbacks)),
                               users=str(len(users)))
    else:
        logout_user()
        abort(401)


@admin.route('/tours_management')  # Управление турами(страница со всеми турами)
def tours_management():
    db_sess = create_session()
    last_tour = None

    tours = db_sess.query(Tour).all()

    tours = [tours[i:i + 2] for i in range(0, len(tours), 2)]  # Формируем туры по парам чтобы расположить на странице
    if tours and len(tours[-1]) % 2:  # Если в последнюю пару попал один тур, записываем его в отдельную переменную
        last_tour, tours = tours[-1], tours[:-1]
    return render_template("admin/tours_manage.html", tours=tours, last_tour=last_tour)


@admin.route('/add_tour', methods=["GET", 'POST'])  # Добавление нового тура
def add_tour():
    form = TourForm()

    db_sess = create_session()
    next_id = str(len(db_sess.query(Tour).all()))

    if request.method == "POST" and form.validate_on_submit():
        pic_path = f'static/img/pic_for_tour_{next_id}.jpg'
        form.file.data.save(pic_path)  # Сохраняем прикрепленное фото
        # Post-запрос к api
        post("http://localhost:5000/api/tours", json={"name": form.name.data,
                                                      "description": form.description.data,
                                                      "start_date": str(form.start_date.data),
                                                      "end_date": str(form.end_date.data),
                                                      "price": form.price.data,
                                                      "image": "/" + pic_path,
                                                      "full_description": form.full_description.data,
                                                      "arrival": form.arrival.data,
                                                      "location": form.location.data,
                                                      "go_back": form.go_back.data}).json()
        return redirect("/admin/tours_management")
    return render_template("admin/add_tour.html", form=form, title="Добавить тур", sbmt="Добавить тур")


@admin.route('/edit_tour/<int:tour_id>', methods=["GET", 'POST'])  # Редактирование тура
def edit_tour(tour_id):
    form = TourForm()
    tour = get(f"http://localhost:5000/api/tours/{tour_id}").json()["tour"]  # Получение тура через api

    if request.method == "GET":  # Устанавливаем значения
        form.name.data = tour["name"]
        form.description.data = tour["description"]
        form.start_date.data = datetime.datetime.strptime(tour["start_date"], '%Y-%m-%d %H:%M:%S').date()
        form.end_date.data = datetime.datetime.strptime(tour["end_date"], '%Y-%m-%d %H:%M:%S').date()
        form.price.data = int(''.join(tour["price"].split())) if type(tour["price"]) != int else tour["price"]
        form.full_description.data = tour["full_description"]
        form.arrival.data = tour["arrival"]
        form.location.data = tour["location"]
        form.go_back.data = tour["go_back"]

    if form.validate_on_submit():
        if form.file.data:  # Если меняют картинку
            pic_path = f'static/img/pic_for_tour_{tour_id}.jpg'
            form.file.data.save(pic_path)  # Сохраняем прикрепленное фото
        else:
            pic_path = tour["image"]

        if pic_path[0] != "/":
            pic_path = "/" + pic_path

        # Post-запрос к api
        post(f"http://localhost:5000/api/tours/{tour_id}", json={"name": form.name.data,
                                                                 "description": form.description.data,
                                                                 "start_date": str(form.start_date.data),
                                                                 "end_date": str(form.end_date.data),
                                                                 "price": form.price.data,
                                                                 "image": pic_path,
                                                                 "full_description": form.full_description.data,
                                                                 "arrival": form.arrival.data,
                                                                 "location": form.location.data,
                                                                 "go_back": form.go_back.data}).json()
        return redirect("/admin/tours_management")
    return render_template("admin/add_tour.html", form=form, title="Редактировать тур", sbmt="Сохранить")


@admin.route('/delete_tour/<int:tour_id>', methods=["GET", 'POST'])  # Удаление тура
def delete_tour(tour_id):
    delete(f"http://localhost:5000/api/tours/{tour_id}")
    return redirect("/admin/tours_management")


class Form(FlaskForm):
    submit = SubmitField("Подтвердить")


@admin.route('/confirmation_delete/<int:tour_id>')  # Подтвержение удаления
def confirmation_delete(tour_id):
    form = Form()
    # if form.validate_on_submit():
    #     return redirect(f"/delete_tour/{tour_id}")
    return render_template("admin/confirmation_delete.html", form=form)


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


@admin.route('/users_management')  # Управление пользователями(страница со всеми турами)
def users_management():
    db_sess = create_session()
    users = db_sess.query(User).all()
    users = [[i, len(i.feedbacks)] for i in users]  # Пользователи и количество их отзывов
    return render_template("admin/users_manage.html", users=users)


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
            change_admin(True)
            return redirect("./")
        return render_template('admin/login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('admin/login.html', form=form)


@admin.errorhandler(401)  # Ошибка авторизации
def not_authenticated(_):
    return redirect("./login")
