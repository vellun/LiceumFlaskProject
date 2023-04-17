import sqlite3

from flask import Flask, render_template, redirect, request, jsonify
from flask_login import LoginManager, login_required, logout_user, current_user
from flask_restful import Api

from admin.admin import admin, change_admin
from api.tours_api import tour_resource
from auth.auth import auth
from data.app_form import AppForm
from data.db_session import global_init, create_session
from data.feedbacks_form import Feedback
from data.register_form import RegisterForm
from data.tours_form import Tour
from data.upload_form import UploadForm
from data.users_form import User
from data.write_feedback_form import WriteFeedbackForm

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

CUR_URL = None


# Функция для запоминания предыдущего url страницы
def cur_url(url):
    global CUR_URL
    CUR_URL = url

    with open('data/cur_url.txt', "w", encoding="utf-8") as f:
        f.write(CUR_URL)  # Запись в файл


@login_manager.user_loader
def load_user(user_id):  # Функция для получения пользователя
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():  # Функция для выхода из аккаунта
    logout_user()
    return redirect(CUR_URL)


@app.route('/')  # Главная страница
def main_page():
    change_admin(False)  # Делаем пользователя не админом чтобы при входе в админку попросить авторизоваться
    cur_url(request.base_url)
    return render_template("main_page.html")


@app.route('/search_tours', methods=['GET', 'POST'])
def search():  # Функция для показа всех туров или туров по поиску
    change_admin(False)
    db_sess = create_session()
    last_tour = None

    cur_url(request.base_url)  # Запоминаем url чтобы после добавления в избранное вернуться обратно

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
    global CUR_URL
    db_sess = create_session()
    tour = db_sess.query(Tour).filter(Tour.id == id).first()
    local_user = db_sess.merge(current_user)
    tour.users.append(local_user)  # Добавление пользователя в список к туру
    db_sess.commit()
    return redirect(CUR_URL)


@app.route('/favourites')
@login_required
def favourites():  # Функция для отображения избранных туров
    last_tour = None

    cur_url(request.base_url)
    tours = current_user.tours
    tours = [tours[i:i + 2] for i in range(0, len(tours), 2)]  # Формируем туры по парам чтобы расположить на странице
    if tours and len(tours[-1]) % 2:  # Если в последнюю пару попал один тур, записываем его в отдельную переменную
        last_tour, tours = tours[-1], tours[:-1]
    return render_template("all_tours.html", tours=tours, last_tour=last_tour, favs=True)


@app.route('/fav_delete/<int:tour_id>')
@login_required
def fav_delete(tour_id):  # Функция для удаления тура из избранного

    db_sess = create_session()
    del_tour = list(filter(lambda x: x.id == tour_id, current_user.tours))[0]

    current_user.tours.remove(del_tour)  # Удаление из списка
    db_sess.merge(current_user)
    db_sess.commit()

    return redirect("/favourites")


@app.route('/more_detailed/<int:id>')
def more_detailed(id):  # Подробнее о туре
    change_admin(False)
    cur_url(request.base_url)
    db_sess = create_session()
    tour = db_sess.query(Tour).filter(Tour.id == id).first()
    # Индексы чтобы проверить наличие тура в списках
    inds = [i.id for i in current_user.tours] if current_user.is_authenticated else []
    b_inds = [i.id for i in current_user.booked_tours] if current_user.is_authenticated else []
    cur_url(f'/more_detailed/{id}')  # Запоминаем url чтобы после добавления в избранное вернуться обратно

    feedbacks = tour.feedbacks  # Отзывы о туре
    feedbacks = [[i, i.pics.split(';') if i.pics else []] for i in feedbacks]  # Список из отзывов и картинок к ним
    feedbacks.reverse()

    return render_template("more_detailed.html", tour=tour, inds=inds, b_inds=b_inds, feedbacks=feedbacks)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    cur_url("/")
    tours = current_user.tours
    return render_template("profile.html", tours=tours)


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
            set_values()
            return render_template("edit_profile.html", form=form, upload_form=upload_form,
                                   message="Ошибка. Загрузите фото")
        upload_form.file.data.save(
            f'static/img/user_imgs/user_{current_user.id}_avatar.jpg')  # Сохраняем новое фото профиля
        db_sess = create_session()
        current_user.avatar = f'/static/img/user_imgs/user_{current_user.id}_avatar.jpg'  # Меняем фото профиля
        db_sess.merge(current_user)
        db_sess.commit()
        set_values()

    return render_template("edit_profile.html", form=form, upload_form=upload_form)


@app.route('/about_us')
def about_us():
    cur_url(request.base_url)
    return render_template("about_us.html")


@app.route("/send_app_form/<int:tour_id>", methods=["GET", "POST"])
@login_required
def send_app_form(tour_id):  # Отправка заявки на участие в туре
    db_sess = create_session()
    tour = db_sess.query(Tour).get(tour_id)
    cur_url(request.base_url)
    form = AppForm()
    if request.method == 'GET':
        form.email.data = current_user.email
    if form.validate_on_submit():
        sqlite_connection = sqlite3.connect('db/travel_agency.db')
        cursor = sqlite_connection.cursor()

        # Добавляем данные в таблицу с помощью sqlite
        sqlite_insert_query = f"""INSERT INTO users_to_booked_tours
                                  (users_who_booked, booked_tours)
                                  VALUES ({current_user.id}, {tour.id});"""
        cursor.execute(sqlite_insert_query)
        sqlite_connection.commit()
        cursor.close()
        return redirect("/booking")
    return render_template("send_app_form.html", form=form, tour=tour)


@app.route("/booking")  # Сообщение после отправления заявки
def booking():
    cur_url(request.base_url)
    return render_template("booking.html")


@app.route("/booked_tours")  # Забронированные полеты
def booked_tours():
    cur_url(request.base_url)
    return render_template("booked_tours.html")


@app.route("/cancel_booking/<int:tour_id>")
def cancel_booking(tour_id):
    db_sess = create_session()
    del_tour = list(filter(lambda x: x.id == tour_id, current_user.booked_tours))[0]

    current_user.booked_tours.remove(del_tour)  # Удаление из списка броней
    db_sess.merge(current_user)
    db_sess.commit()
    return redirect("/cancel_booking_message")


@app.route("/cancel_booking_confirmation/<int:tour_id>")  # Подтверждение отмены брони
def cancel_booking_conf(tour_id):
    return render_template("cancel_booking_conf.html", tour_id=tour_id)


@app.route("/cancel_booking_message")  # Подтверждение отмены брони
def cancel_booking_mess():
    return render_template("cancel_booking_mess.html")


@app.route("/write_feedback/<int:tour_id>", methods=["GET", "POST"])
@login_required
def write_feedback(tour_id):  # Отзыв
    global CUR_URL
    form = WriteFeedbackForm()
    db_sess = create_session()
    tour = db_sess.query(Tour).get(tour_id)
    paths = []
    if form.validate_on_submit():

        feedback = Feedback(scoring=form.score.data,  # Создаем отзыв
                            pluses=form.pluses.data,
                            minuses=form.minuses.data,
                            comment=form.comment.data,
                            author_id=current_user.id,
                            tour_id=tour_id)

        db_sess.add(feedback)
        db_sess.commit()

        files = form.file.data
        for i in range(len(files)):
            if files[i] and not files[i].filename.split(".")[-1] in ["jpg", "jpeg", "png", "gif"]:  # Если выбранный файл не фото
                return render_template("write_feedback.html", tour=tour, form=form, message="Ошибка. Загрузите фото")
            files[i].save(
                f'static/img/feedbacks_pics/user_{current_user.id}_tour_{tour.id}_feedback_{feedback.id}_{i}.jpg')  # Сохраняем фото отзыва
            paths.append(
                f'/static/img/feedbacks_pics/user_{current_user.id}_tour_{tour.id}_feedback_{feedback.id}_{i}.jpg')

        feedback.pics = ';'.join(paths)
        db_sess.commit()

        f = open('data/cur_url.txt', "r", encoding="utf-8")
        return redirect(f.readline())
    return render_template("write_feedback.html", tour=tour, form=form)


@app.route('/feedbacks', methods=['GET', 'POST'])
def feedbacks():  # Отзывы
    cur_url(request.base_url)
    db_sess = create_session()
    feedbacks = db_sess.query(Feedback).all()
    feedbacks = [[i, i.pics.split(';') if i.pics else []] for i in feedbacks]  # Список из отзывов и картинок к ним
    feedbacks.reverse()  # Переворачиваем список чтобы сверху отображались свежие отзывы

    return render_template("feedbacks.html", feedbacks=feedbacks)


@app.errorhandler(500)
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(401)  # Ошибка аутентификации
def not_authenticated(_):
    # cur_url(request.base_url)
    return redirect("/auth/login")


def main():
    app.run(port=5000, host="127.0.0.1")


if __name__ == '__main__':
    main()
