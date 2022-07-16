import sqlite3

import sqlalchemy
from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from werkzeug.exceptions import BadRequest
import utils

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


# сериализация моделей
class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

# настройка rest-x
api = Api(app)

movie_ns = api.namespace("movies")
director_ns = api.namespace("directors")
genre_ns = api.namespace("genres")


# группа эндпоинтов movies
@movie_ns.route("/")
class MoviesView(Resource):
    def get(self):

        if not request.args:
            return utils.get_all_universal(Movie, movies_schema)

        elif 'genre_id' in request.args.keys() and 'director_id' in request.args.keys():
            genre_id = request.args['genre_id']
            director_id = request.args['director_id']
            all_movies = db.session.query(Movie).filter(Movie.genre_id == genre_id,
                                                        Movie.director_id == director_id).all()
            return movies_schema.dump(all_movies), 200

        elif 'director_id' in request.args:
            director_id = request.args['director_id']
            all_movies = db.session.query(Movie).filter(Movie.director_id == director_id).all()
            return movies_schema.dump(all_movies), 200

        elif 'genre_id' in request.args:
            genre_id = request.args['genre_id']
            all_movies = db.session.query(Movie).filter(Movie.genre_id == genre_id).all()
            return movies_schema.dump(all_movies), 200

    def post(self):
        return utils.post_universal(Movie)


@movie_ns.route("/<int:uid>")
class MovieView(Resource):
    def get(self, uid):
        return utils.get_by_id_universal(uid, Movie, movie_schema)

    def put(self, uid):
        try:
            input_data = request.json
            item = db.session.query(Movie).filter(Movie.id == uid).one()
        except Exception as e:
            return str(e), 404

        item.title = input_data.get('title')
        item.description = input_data.get('description')
        item.trailer = input_data.get('trailer')
        item.year = input_data.get('year')
        item.rating = input_data.get('rating')
        item.genre_id = input_data.get('genre_id')
        item.director_id = input_data.get('director_id')

        db.session.add(item)
        db.session.commit()
        db.session.close()

        return "", 204

    def patch(self, uid):
        return utils.patch_universal(uid, Movie)

    def delete(self, uid):
        return utils.delete_universal(uid, Movie)


# группа эндпоинтов directors
@director_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        return utils.get_all_universal(Director, directors_schema)

    def post(self):
        return utils.post_universal(Director)


@director_ns.route("/<int:uid>")
class DirectorView(Resource):
    def get(self, uid):
        return utils.get_by_id_universal(uid, Director, director_schema)

    def patch(self, uid):
        return utils.patch_universal(uid, Director)

    def put(self, uid):
        try:
            input_data = request.json
            item = db.session.query(Director).filter(Director.id == uid).one()
        except Exception as e:
            return str(e), 404

        item.name = input_data.get('name')

        db.session.add(item)
        db.session.commit()
        db.session.close()

        return "", 204

    def delete(self, uid):
        return utils.delete_universal(uid, Director)


# группа эндпоинтов genres
@genre_ns.route("/")
class GenresView(Resource):
    def get(self):
        return utils.get_all_universal(Genre, genres_schema)

    def post(self):
        return utils.post_universal(Genre)


@genre_ns.route("/<int:uid>")
class GenreView(Resource):
    def get(self, uid):
        return utils.get_by_id_universal(uid, Genre, genre_schema)

    def patch(self, uid):
        return utils.patch_universal(uid, Genre)

    def put(self, uid):
        try:
            input_data = request.json
            item = db.session.query(Genre).filter(Genre.id == uid).one()
        except Exception as e:
            return str(e), 404

        item.name = input_data.get('name')

        db.session.add(item)
        db.session.commit()
        db.session.close()

        return "", 204

    def delete(self, uid):
        return utils.delete_universal(uid, Genre)


if __name__ == '__main__':
    app.run(debug=True)
