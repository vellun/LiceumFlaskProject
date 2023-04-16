import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from data.db_session import SqlAlchemyBase

users_to_tours = sqlalchemy.Table(  # Вспомогательная таблица(для избранных туров)
    'users_to_tours',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('users', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('tours', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('tours.id')))

users_to_booked_tours = sqlalchemy.Table(  # Вспомогательная таблица(для забронированных туров)
    'users_to_booked_tours',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('users_who_booked', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('booked_tours', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('tours.id')))


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    avatar = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)

    feedbacks = orm.relationship("Feedback", back_populates='author')  # Список отзывов пользователя

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
