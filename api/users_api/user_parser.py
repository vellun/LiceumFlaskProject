from flask_restful import reqparse

user_parser = reqparse.RequestParser()
user_parser.add_argument('id', type=int)
user_parser.add_argument('name')
user_parser.add_argument('surname')
user_parser.add_argument('email')
