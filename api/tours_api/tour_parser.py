from flask_restful import reqparse

tour_parser = reqparse.RequestParser()
tour_parser.add_argument('id', type=int)
tour_parser.add_argument('name')
tour_parser.add_argument('description', type=str)
tour_parser.add_argument("full_description")
tour_parser.add_argument('start_date')
tour_parser.add_argument('end_date')
tour_parser.add_argument('image')
tour_parser.add_argument('price')
tour_parser.add_argument("arrival")
tour_parser.add_argument("location")
tour_parser.add_argument("go_back")
