from fastapi import APIRouter, Body

from db.session import connect


user_view = APIRouter()


@user_view.get("/users", tags=["users"])
def get_users():
    connection = connect()
    cursor = connection.cursor()
    sql = """SELECT json_agg(to_json(row))
             FROM (SELECT *
             FROM user_table) row"""

    cursor.execute(sql)

    ex = cursor.fetchone()[0]

    output_json = {
        "data": [],
        "status": 0
    }

    output_json["data"] = ex

    return output_json
    

@user_view.get("/users/{id}", tags=["users"])
def get_users(id: int):
    connection = connect()
    cursor = connection.cursor()
    sql = """SELECT json_agg(to_json(row))
             FROM (SELECT *
             FROM user_table) row
             WHERE id = %s"""
    cursor.execute(sql, (id,))
    ex = cursor.fetchone()[0]

    output_json = {
        "data": ex,
        "status": 0
    }

    return output_json


@user_view.put("/users", tags=["users"])
def update_user(id: int = Body(default=None), money: int = Body(default=None)):
    
    # if user.role not in ["buyer", "seller", "manager", "help", "operator"]:
    #     return {"message": "Invalid role", "status": 1}
    
    print(id)
    print(money)

    connection = connect()
    cursor = connection.cursor()
    sql = """UPDATE user_table
             set
             balance = balance + %s
             where id = %s
             """

    # print(id, money)
    cursor.execute(sql, (money, id))

    connection.commit()
    cursor.close()
    connection.close()

    return {"message": "User updated!", "status": 2}


@user_view.delete("/users/{id}", tags=["users"])
def delete_user(id: int):
    connection = connect()
    cursor = connection.cursor()
    sql = """DELETE FROM white_list_table
             WHERE id_user = %s"""
    cursor.execute(sql, (id,))

    sql = """DELETE FROM user_table
             WHERE id = %s"""
    cursor.execute(sql, (id,))

    connection.commit()
    cursor.close()
    connection.close()

    return {"message": "User deleted", "status": 2}


@user_view.post("/users_update", tags=["users"])
def update_user(id: int = Body(default=None), money: int = Body(default=None)):
    
    # if user.role not in ["buyer", "seller", "manager", "help", "operator"]:
    #     return {"message": "Invalid role", "status": 1}
    
    print(id)
    print(money)

    connection = connect()
    cursor = connection.cursor()
    sql = """UPDATE user_table
             set
             balance = balance + %s
             where id = %s
             """

    # print(id, money)
    cursor.execute(sql, (money, id))

    connection.commit()
    cursor.close()
    connection.close()

    return {"message": "User updated!", "status": 2}
