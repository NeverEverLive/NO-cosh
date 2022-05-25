from fastapi import APIRouter, Body
from datetime import datetime, timedelta

from model import UserLoginSchema, UserSchema
from db.session import connect
from .jwt_handler import signJWT


auth_view = APIRouter()


@auth_view.post("/users/signup", tags=["auth_users"])
def user_signup(user: UserSchema = Body(default=None)):
    # connection = None
    # cursor = None
    connection = connect()
    cursor = connection.cursor()
    try:
        print(user.login)
        print(user.role)
        if user.role not in ["buyer", "seller", "manager", "help", "operator"]:
            return {"message": "Invalid role", "status": 1}

        sql = """
                insert into user_table(login, password, name, lat, lon, phone, role, balance)
                values(%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(sql, (user.login, user.password, user.name, user.latitude, user.longitude, user.phone, user.role, 0))

        sql = """SELECT id
                 from user_table
                 order by id desc
                 limit 1"""

        cursor.execute(sql)

        ex = cursor.fetchone()[0]
        count = ex

        print(count)

        sql = """
                insert into white_list_table(access_token, date_acc, date_ref, refresh_token, id_user)
                values(%s,%s,%s,%s,%s)
        """

        tokens = signJWT(user.login)
        print(tokens)

        ex = cursor.execute(sql, (tokens['access_token'], str(datetime.now()), str(datetime.now()), tokens['refresh_token'], count))    

        print("Executed", ex)
        
    except Exception as error:
        return {"message": str(error), "status": 0}
    finally:
        connection.commit()
        cursor.close()
        connection.close()
    
    return {"data": tokens, "message": "User created!", "status": 0}
    

def check_user(data: UserLoginSchema):
    # добавить проверку на то что токен не в whitelist'е
    # print(user.login, user.password)
    connection = connect()
    cursor = connection.cursor()
    sql = """SELECT json_agg(to_json(row))
             FROM (SELECT *
             from user_table) row"""

    cursor.execute(sql)
    ex = cursor.fetchone()[0]
    
    connection.commit()
    cursor.close()
    connection.close()

    for user in ex:
        print(data.login, data.password)
        print(user['login'], user['password'])
        if user['login'] == data.login and user['password'] == data.password:
            return True
        return False


@auth_view.post("/users/login", tags=["auth_users"])
def user_login(user: UserLoginSchema = Body(default=None)):
    if check_user(user):
        connection = connect()
        cursor = connection.cursor()

        sql = """
                insert into white_list_table(access_token, date_acc, date_ref, refresh_token, id_user)
                values(%s,%s,%s,%s,%s)
        """

        tokens = signJWT(user.login)
        print(tokens)

        cursor.execute(sql, (tokens['access_token'], str(datetime.now()), str(datetime.now()), tokens['refresh_token'], user.id))    

        return signJWT(user.login)
    else:
        return {
            "error": "Invalid login details"
        }


@auth_view.post("users/logout", tags=["auth_users"])
def user_logout(user: UserLoginSchema = Body(default=None)):
    connection = connect()
    cursor = connection.cursor()
    
    sql = """DELETE FROM white_list_table
                WHERE id_user = %s"""
    cursor.execute(sql, (user.id,))
    pass


def check_access_token(token):
    connection = connect()
    cursor = connection.cursor()

    sql = """SELECT date_acc
             FROM white_list_table
             WHERE refresh_token = %s
             order by id desc
             limit 1"""

    cursor.execute(sql, (token,))
    ex = cursor.fetchone()[0]

    date = ex

    print(date)

    if datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S.%f") + timedelta(days=1) < datetime.now():
        sql = """DELETE FROM white_list_table
                 WHERE refresh_token = %s"""
        
        cursor.execute(sql, (token,))
        return False

    return True


def refresh(token: str):
    try:
        connection = connect()
        cursor = connection.cursor()

        sql = """SELECT id, id_user, access_token, refresh_token, date_acc, date_ref
                FROM white_list_table
                WHERE refresh_token = %s
                order by id desc
                limit 1"""
        
        cursor.execute(sql, (token,))
        ex = cursor.fetchone()

        print("ex", ex)

        id = ex[0]
        user_id = ex[1]

        sql = """SELECT login
                FROM user_table
                WHERE id = %s
                limit 1"""

        cursor.execute(sql, (user_id,))
        login = cursor.fetchone()[0]

        print(login)

        sql = """DELETE FROM white_list_table
                WHERE id = %s"""
        cursor.execute(sql, (id,))

        tokens = signJWT(login)

        print(tokens)

        print(ex[2],ex[4],ex[3],ex[5], sep= '\n')

        sql = """
                    insert into white_list_table(access_token, date_acc, date_ref, refresh_token, id_user)
                    values(%s,%s,%s,%s,%s)
            """
        cursor.execute(sql, (ex[2],ex[4],ex[5],ex[3],user_id))
    except Exception as error:
        return {"message": str(error), "status": 1}
    finally:
        connection.commit()
        cursor.close()
        connection.close()
    
    return tokens
