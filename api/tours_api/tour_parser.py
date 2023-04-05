from flask_restful import reqparse

user_parser = reqparse.RequestParser()
user_parser.add_argument('id', type=int)
user_parser.add_argument('name')
user_parser.add_argument('discription')
user_parser.add_argument('start_date')
user_parser.add_argument('end_date')
user_parser.add_argument('image')
user_parser.add_argument('price')