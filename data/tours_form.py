import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase

users_to_tours = sqlalchemy.Table(  # Вспомогательная таблица тк отношение многие ко многим
    'users_to_tours',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('users', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('tours', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('tours.id'))
)


class Tour(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tours'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    discription = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    full_description = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    feedbacks = orm.relationship("Feedback", back_populates='tour')  # Список отзывов о туре
