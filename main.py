from flask import Flask, render_template, redirect, request, abort, jsonify
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
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


@app.route('/all_tours')
def all_tours():
    db_sess = create_session()
    tours, last_tour = db_sess.query(Tour).all(), None
    tours = [tours[i:i + 2] for i in range(0, len(tours), 2)]  # Формируем туры по парам чтобы расположить на странице
    if len(tours[-1]) % 2:
        last_tour, tours = tours[-1], tours[:-1]
    return render_template("all_tours.html", tours=tours, last_tour=last_tour)


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
def error_404(error):
    return jsonify({"error": 'Address not found'})


if __name__ == '__main__':
    app.run(port=5000, host="127.0.0.1")
