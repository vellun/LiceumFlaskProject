import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Feedback(SqlAlchemyBase, SerializerMixin):  # Форма отзыва
    __tablename__ = 'feedbacks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    scoring = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)  # Оценка от 1 до 5
    pluses = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # Содержание отзыва
    minuses = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    comment = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pics = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # Список из прикрепленных картинок
    date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True,
                             default=datetime.datetime.now())  # Дата написания отзыва

    author_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey("users.id"))  # Автор отзыва(id пользователя)
    author = orm.relationship("User")  # Автор отзыва(объект класса User)

    tour_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("tours.id"))  # Тур, про который отзыв(id)
    tour = orm.relationship("Tour")  # Тур, про который отзыв(объект класса Tour)
