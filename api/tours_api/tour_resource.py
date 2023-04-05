from flask import jsonify, request
from flask_restful import Resource, abort

from api.users_api.user_parser import user_parser
from data import db_session
from data.tours_form import Tour
from data.users_form import User


def abort_if_tours_not_found(tour_id):
    session = db_session.create_session()
    tours = session.query(Tour).get(tour_id)
    if not tours:
        abort(404, message=f"Tour {tour_id} not found")


class TourResourse(Resource):
    def get(self, tour_id):  # Получение тура
        db_sess = db_session.create_session()
        tour = db_sess.query(Tour).get(tour_id)
        if not tour:
            abort_if_tours_not_found(tour_id)
        return jsonify(
            {"tour": tour.to_dict(only=("id", "name", "discription", "start_date", "end_date", "image", "price"))})

    def delete(self, tour_id):  # Удаление тура
        db_sess = db_session.create_session()
        tour = db_sess.query(Tour).get(tour_id)
        if not tour:
            abort_if_tours_not_found(tour_id)
        db_sess.delete(tour)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    def post(self, tour_id):  # Редактирование тура
        db_sess = db_session.create_session()
        tour = db_sess.query(Tour).get(tour_id)
        if not tour:
            abort_if_tours_not_found(tour_id)
        args = user_parser.parse_args()
        if "name" in request.json:
            tour.name = args["name"]
        if "discription" in request.json:
            tour.discription = args["discription"]
        if "start_date" in request.json:
            tour.start_date = args["start_date"]
        if "end_date" in request.json:
            tour.end_date = args["end_date"]
        if "price" in request.json:
            tour.price = args["price"]
        db_sess.commit()
        return jsonify({'success': 'OK'})


class ToursList(Resource):
    def get(self):  # Получение туров
        db_sess = db_session.create_session()
        tours = db_sess.query(Tour).all()
        return jsonify(
            {"tours": [item.to_dict(only=("id", "name", "discription", "start_date", "end_date", "image", "price"))
                       for item in tours]})

    def post(self):  # Добавление тура
        args = user_parser.parse_args()
        db_sess = db_session.create_session()
        tour = User(
            name=args["name"],
            discription=args["discription"],
            start_date=args["start_date"],
            end_date=args["end_date"],
            image=args["image"],
            price=args["price"]
        )
        db_sess.add(tour)
        db_sess.commit()
        return jsonify({'success': 'OK'})
