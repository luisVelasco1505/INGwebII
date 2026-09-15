from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            if get_jwt().get('role') not in roles:
                return jsonify(error='No tenés permisos para realizar esta acción'), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator
