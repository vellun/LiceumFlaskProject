import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Tour(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tours'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    full_description = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    users = orm.relationship("User", secondary="users_to_tours",
                             backref="tours", lazy='subquery')  # Атрибут для получения списка туров пользователя

    feedbacks = orm.relationship("Feedback", back_populates='tour')  # Список отзывов о туре
