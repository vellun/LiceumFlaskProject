from flask import jsonify, request
from flask_restful import Resource, abort

from data import db_session
from api.users_api.user_parser import user_parser
from data.users_form import User


def abort_if_users_not_found(users_id):
    session = db_session.create_session()
    users = session.query(User).get(users_id)
    if not users:
        abort(404, message=f"User {users_id} not found")


class UserResourse(Resource):
    def get(self, user_id):  # Получение пользователя
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        if not user:
            abort_if_users_not_found(user_id)
        return jsonify({"user": user.to_dict(only=("id", "surname", "name", "email", "avatar"))})

    def delete(self, user_id):  # Удаление пользователя
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        if not user:
            abort_if_users_not_found(user_id)
        db_sess.delete(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    def post(self, user_id):  # Редактирование пользователя
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        if not user:
            abort_if_users_not_found(user_id)
        args = user_parser.parse_args()
        if "name" in request.json:
            user.name = args["name"]
        if "surname" in request.json:
            user.surname = args["surname"]
        if "email" in request.json:
            user.email = args["email"]
        db_sess.commit()
        return jsonify({'success': 'OK'})


class UsersList(Resource):
    def get(self):  # Получение пользователей
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        return jsonify({"users": [item.to_dict(only=("id", "surname", "name", "email", "avatar"))
                                  for item in users]})

    def post(self):  # Добавление пользователя
        args = user_parser.parse_args()
        db_sess = db_session.create_session()
        user = User(
            name=args["name"],
            surname=args["surname"],
            email=args["email"]
        )
        db_sess.add(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})