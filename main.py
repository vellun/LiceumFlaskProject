from flask import Flask, render_template, redirect, request, jsonify
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_wtf import FlaskForm
from wtforms import FileField

from data.db_session import global_init, create_session
from data.login_form import LoginForm
from data.register_form import RegisterForm
from data.tours_form import Tour
from data.users_form import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
global_init("db/travel_agency.db")

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):  # Функция для получения пользователя
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
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


class UploadForm(FlaskForm):
    file = FileField()


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
    return render_template("profile.html", form=form, img=None)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    pass


@app.route('/register', methods=['GET', 'POST'])
def reqister():
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
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(401)
def not_authenticated(_):
    return redirect("/login")


if __name__ == '__main__':
    app.run(port=5000, host="127.0.0.1")
