from flask import jsonify


def bad_request(message):
    return jsonify(error=message), 400


def not_found(message='Recurso no encontrado'):
    return jsonify(error=message), 404
