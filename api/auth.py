from datetime import datetime, timedelta
import functools

from flask import request

import jwt

from api import app


def jwt_required(func):
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        try:
            type, token = request.headers.get('Authentication').split(" ")
            payload = decode_auth_token(token)

            _globals = func.__globals__
            oldvalue = _globals.get('payload', None)
            _globals['payload'] = payload

            try:
                res = func(*args, **kwargs)
            finally:
                if oldvalue is None:
                    del _globals['payload']
                else:
                    _globals['payload'] = oldvalue

        except jwt.ExpiredSignatureError:
            return {"message": "Token Expired"}, 401
        except jwt.DecodeError:
            return {"message": "Token Invalid"}, 401
        except jwt.InvalidTokenError:
            return {"message": "Token Invalid"}, 401

        return res

    return wrapper


def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=60),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except BaseException as err:
        return err


def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
    return payload['sub']
