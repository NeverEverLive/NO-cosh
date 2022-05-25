import time
import jwt
from decouple import config


JWT_SECRET_ACCESS = config("secret_access")
JWT_SECRET_REFRESH = config("secret_refresh")
JWT_ALGORITHM = config("algorithm")

ACCESS_TOKEN_LIFETIME = 30
REFRESH_TOKEN_LIFETIME = 30


def token_response(access_token: str, refresh_token: str):
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def signJWT(userID: str):
    payload = {
        "userID": userID,
        "expiry": time.time() + 600
    }
    access_token = jwt.encode(payload, JWT_SECRET_ACCESS, algorithm=JWT_ALGORITHM)
    refresh_token = jwt.encode(payload, JWT_SECRET_REFRESH, algorithm=JWT_ALGORITHM)
    return token_response(access_token, refresh_token)


def decodeJWT(access_token: str, refresh_token: str):
    try:
        decode_token = {
            "access_token": jwt.decode(access_token, JWT_SECRET_ACCESS, algorithm = JWT_ALGORITHM),
            "refresh_token": jwt.decode(refresh_token, JWT_SECRET_REFRESH, algorithms=JWT_ALGORITHM)
        }
        return decode_token if decode_token["access_token"]['expires'] >= time.time() else None
    except Exception as error:
        return {
            "message": str(error),
            "status": 1
        }
