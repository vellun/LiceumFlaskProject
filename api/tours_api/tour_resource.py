import datetime
import os

from flask import jsonify, request
from flask_restful import Resource, abort

from api.tours_api.tour_parser import tour_parser
from data import db_session
from data.tours_form import Tour


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
            {"tour": tour.to_dict(
                only=("id", "name", "description", "full_description", "start_date", "end_date", "image", "price",
                      "arrival", "location", "go_back"))})

    def delete(self, tour_id):  # Удаление тура
        db_sess = db_session.create_session()
        tour = db_sess.query(Tour).get(tour_id)

        try:
            os.remove(tour.image[1:])  # Удаляем картинку тура
        except:
            pass

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
        args = tour_parser.parse_args()

        #  Преобразование строк в объекты datetime
        start_date = datetime.datetime.strptime(args["start_date"], '%Y-%m-%d')
        end_date = datetime.datetime.strptime(args["end_date"], '%Y-%m-%d')

        price = '{0:,}'.format(int(args["price"])).replace(',', ' ')  # Цена, разделенная на разряды

        if "name" in request.json:
            tour.name = args["name"]
        if "description" in request.json:
            tour.description = args["description"]
        if "full_description" in request.json:
            tour.full_description = args["full_description"]
        if "start_date" in request.json:
            tour.start_date = start_date
        if "end_date" in request.json:
            tour.end_date = end_date
        if "price" in request.json:
            tour.price = price
        if "image" in request.json:
            tour.image = args["image"]
        if "arrival" in request.json:
            tour.arrival = args["arrival"]
        if "location" in request.json:
            tour.location = args["location"]
        if "go_back" in request.json:
            tour.go_back = args["go_back"]
        db_sess.commit()
        return jsonify({'success': 'OK'})


class ToursList(Resource):
    def get(self):  # Получение туров
        db_sess = db_session.create_session()
        tours = db_sess.query(Tour).all()
        return jsonify(
            {"tours": [item.to_dict(
                only=(
                    "id", "name", "description", "full_description", "start_date", "end_date", "image", "price",
                    "arrival", "location", "go_back"))
                for item in tours]})

    def post(self):  # Добавление тура
        args = tour_parser.parse_args()
        db_sess = db_session.create_session()

        #  Преобразование строк в объекты datetime
        start_date = datetime.datetime.strptime(args["start_date"], '%Y-%m-%d')
        end_date = datetime.datetime.strptime(args["end_date"], '%Y-%m-%d')

        price = '{0:,}'.format(int(args["price"])).replace(',', ' ')  # Цена, разделенная на разряды

        tour = Tour(
            name=args["name"],
            description=args["description"],
            start_date=start_date,
            end_date=end_date,
            image=args["image"],
            price=price,
            full_description=args["full_description"],
            arrival=args["arrival"],
            location=args["location"],
            go_back=args["go_back"]
        )
        db_sess.add(tour)
        db_sess.commit()
        print({'success': 'OK'})
        return jsonify({'success': 'OK'})
