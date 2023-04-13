from flask import Flask, render_template, redirect, request, jsonify
from flask_login import LoginManager, login_required, logout_user, current_user
from flask_restful import Api

from api.tours_api import tour_resource
from auth.auth import auth
from admin.admin import admin
from data.db_session import global_init, create_session
from data.register_form import RegisterForm
from data.tours_form import Tour
from data.upload_form import UploadForm
from data.users_form import User

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
global_init("db/travel_agency.db")

login_manager = LoginManager()
login_manager.init_app(app)

app.register_blueprint(auth, url_prefix='/auth')  # Регистрация Blueprint(вход и регистрация)
app.register_blueprint(admin, url_prefix='/admin')  # Регистрация Blueprint(админка)

# Добавление ресурсов api
api.add_resource(tour_resource.ToursList, '/api/tours')  # для списка туров
api.add_resource(tour_resource.TourResourse, '/api/tours/<int:tour_id>')  # для одного тура


@login_manager.user_loader
def load_user(user_id):  # Функция для получения пользователя
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():  # Функция для выхода из аккаунта
    logout_user()
    return redirect("/")


@app.route('/')  # Главная страница
def main_page():
    return render_template("main_page.html")


@app.route('/search_tours', methods=['GET', 'POST'])
def search():  # Функция для показа всех туров или туров по поиску
    db_sess = create_session()
    last_tour = None

    if request.method == 'GET':  # Если нужно получить все туры
        tours = db_sess.query(Tour).all()
    else:  # Если воспользовались поиском по турам
        tours = db_sess.query(Tour).filter(Tour.name.like(f"%{request.form['search'].capitalize()}%")).all()
    tours = [tours[i:i + 2] for i in range(0, len(tours), 2)]  # Формируем туры по парам чтобы расположить на странице
    if tours and len(tours[-1]) % 2:  # Если в последнюю пару попал один тур, записываем его в отдельную переменную
        last_tour, tours = tours[-1], tours[:-1]
    inds = [i.id for i in current_user.tours] if current_user.is_authenticated else []
    return render_template("all_tours.html", tours=tours, last_tour=last_tour, inds=inds)


@app.route('/add_to_favourites/<int:id>')
@login_required
def add_to_favourites(id):  # Функция для добавления тура в избранное
    db_sess = create_session()
    tour = db_sess.query(Tour).filter(Tour.id == id).first()

    current_user.tours.append(tour)

    db_sess.commit()
    return redirect("/search_tours")


@app.route('/more_detailed/<int:id>')
def more_detailed(id):  # Подробнее о туре
    db_sess = create_session()
    tour = db_sess.query(Tour).filter(Tour.id == id).first()
    return render_template("more_detailed.html", tour=tour)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = UploadForm()

    if form.validate_on_submit():
        if form.file.data.filename.split(".")[-1] in ["jpg", "jpeg", "png", "gif"]:
            form.file.data.save('static/img/user_imgs/user_avatar.jpg')

            db_sess = create_session()
            current_user.avatar = '/static/img/user_imgs/user_avatar.jpg'
            db_sess.merge(current_user)
            db_sess.commit()
    return render_template("profile.html", form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():  # Редактирование профиля пользователя
    form = RegisterForm()
    upload_form = UploadForm()

    def set_values():  # Установка значений из бд в поля для изменения данных
        form.name.data = current_user.name
        form.surname.data = current_user.surname
        form.email.data = current_user.email

    if request.method == "GET":
        set_values()

    if form.is_submitted() and form.submit.data:  # Если сработала форма изменения данных
        db_sess = create_session()
        current_user.name = form.name.data
        current_user.surname = form.surname.data
        current_user.email = form.email.data
        db_sess.merge(current_user)
        db_sess.commit()
        set_values()
        return redirect("profile")

    elif upload_form.validate_on_submit() and upload_form.save.data:  # Если сработала форма изменения фото профиля
        if not upload_form.file.data.filename.split(".")[-1] in ["jpg", "jpeg", "png",
                                                                 "gif"]:  # Если выбранный файл не фото
            # или отправлена пустая форма
            set_values()
            return render_template("edit_profile.html", form=form, upload_form=upload_form,
                                   message="Ошибка. Загрузите фото")
        upload_form.file.data.save('static/img/user_imgs/user_avatar.jpg')  # Сохраняем новое фото профиля
        db_sess = create_session()
        current_user.avatar = '/static/img/user_imgs/user_avatar.jpg'  # Меняем фото профиля
        db_sess.merge(current_user)
        db_sess.commit()
        set_values()

    return render_template("edit_profile.html", form=form, upload_form=upload_form)


@app.route('/about_us')
def about_us():
    return render_template("about_us.html")


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(401)
def not_authenticated(_):
    return redirect("/login")


def main():
    app.run(port=5000, host="127.0.0.1")


if __name__ == '__main__':
    main()
