import sqlalchemy
from flask import request
from werkzeug.exceptions import BadRequest

from app import db


def get_all_universal(class_, schema_):
    all_items = db.session.query(class_).all()
    return schema_.dump(all_items), 200


def post_universal(class_):
    try:
        input_data = request.json
        new_object = class_(**input_data)
        with db.session.begin():
            db.session.add(new_object)
        return "", 201
    except sqlalchemy.exc.IntegrityError:
        return "Был передан уже существующий в базе id", 405
    except (TypeError, BadRequest):
        return "Переданы данные несоответствующего формата", 405
    except Exception as e:
        return str(e), 405


def get_by_id_universal(uid, class_, schema):
    try:
        result = db.session.query(class_).filter(class_.id == uid).one()
        return schema.dump(result), 200
    except Exception as e:
        return str(e), 404


def patch_universal(uid, class_):
    try:
        input_data = request.json
        del input_data['id']  # чтобы в случае передачи id в jsone не изменять его на новый
        db.session.query(class_).filter(class_.id == uid).update(input_data)
        db.session.commit()
        db.session.close()
        return "", 204
    except sqlalchemy.exc.IntegrityError:
        return "Был передан уже существующий в базе id", 405
    except (TypeError, BadRequest):
        return "Переданы данные несоответствующего формата", 405
    except Exception as e:
        return str(e), 405


def delete_universal(uid, class_):
    try:
        item_to_delete = db.session.query(class_).filter(class_.id == uid).one()
    except Exception as e:
        return f"Запись с id {uid} не найдена", 404

    db.session.delete(item_to_delete)
    db.session.commit()
    db.session.close()

    return "", 204
