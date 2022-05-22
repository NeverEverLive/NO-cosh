# main:app --reload
from typing import List, Union, Any

from h11 import ConnectionClosed
from core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body, FastAPI, Depends, Header, Request, UploadFile, File
from api.general_pages.home_page import general_pages_router
from db.session import connect
# from db.base_class import Base
# from db.session import engine, SessionLocal
from model import AdvertisementSchema, Category, CommectSchema, OrderSchema, UserSchema, UserLoginSchema
from api.auth.jwt_handler import signJWT
from api.auth.jwt_bearer import jwtBearer
from datetime import timedelta, datetime
from random import randint as rand
from cloudinary import uploader
import cloudinary

# from db.session import session
# from sqlalchemy import select

def include_router(app):
    app.include_router(general_pages_router)

# POSTGRES_USER = emuxbiigbsdiwr
# POSTGRES_PASSWORD = b6c0405a9b8eb05df613e33abe79abbeb1aa5aea254402b94e178bb61cfb4c95
# POSTGRES_SERVER = ec2-52-86-115-245.compute-1.amazonaws.com
# POSTGRES_PORT = 5432
# POSTGRES_DB = d6g1mar985bj8b

orders = [
    {
        "id": 1,
        "title": "Apple",
        "price": 2
    },
    {
        "id": 2,
        "title": "Orange",
        "price": 4
    }
    
]


users = []



# def create_tables():
#     Base.metadata.create_all(bind=engine)


def start_application():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION) # 
    include_router(app)
    origins = [
    "*"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # create_tables()
    return app




app = start_application()

# @app.get("/orders", tags=['orders'])
# def get_orders():
#     return {"data": orders, "status": 0}


@app.get("/orders/{id}", tags=['orders'])
def get_order(id: int):
    if id > len(orders):
        return {
            "error": "Order with this id does not exist"
        }
    for order in orders:
        if order["id"] == id:
            return {
                "data": order
            }


@app.post("/orders", dependencies=[Depends(jwtBearer())], tags=['orders'])
def add_order(order: OrderSchema):
    order.id = len(orders) + 1
    orders.append(order.dict())
    return {
        "message": "Order created"
    }


@app.post("/users/signup", tags=["users"])
def user_signup(user: UserSchema = Body(default=None)):
    # connection = None
    # cursor = None
    connection = connect()
    cursor = connection.cursor()
    try:
        print(user.login)
        print(user.role)
        if user.role not in ["buyer", "seller", "manager"]:
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
    


# @app.post("/users/signup", tags=["users"])
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



@app.post("/users/login", tags=["users"])
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


@app.post("users/logout", tags=["users"])
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


@app.get("/users", tags=["users"])
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
    

@app.get("/users/{id}", tags=["users"])
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


@app.put("/users/{id}", tags=["users"])
def update_user(id: int, user: UserSchema = Body(default=None)):
    
    if user.role not in ["buyer", "seller", "manager"]:
        return {"message": "Invalid role", "status": 1}
    
    connection = connect()
    cursor = connection.cursor()
    sql = """UPDATE user_table
             set
             login = %s,
             password = %s,
             name = %s,
             phone = %s,
             role = %s,
             lat = %s,
             lon = %s
             where id = %s
             """

    print(user.login, user.password, user.name, user.phone, user.role, user.latitude, user.longitude, id)
    cursor.execute(sql, (user.login, user.password, user.name, user.phone, user.role, user.latitude, user.longitude, id))

    connection.commit()
    cursor.close()
    connection.close()


    return {"message": "User updated!", "status": 2}



@app.delete("/users/{id}", tags=["users"])
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




@app.get("/test_db_orders", tags=["orders"])
def get_all_orders(request: Request):
    print(request.headers.get("refresh_token"))
    if not check_access_token(request.headers.get('refresh_token')):
        return {"message": "Access token is dead", 'status': 1}
    else:
        # refresh(request.headers.get('refresh_token'))
        pass
    try:
        connection = connect()
        # print(settings.POSTGRES_SERVER, 
        # settings.POSTGRES_PORT, 
        # settings.POSTGRES_DB, 
        # settings.POSTGRES_USER, 
        # settings.POSTGRES_PASSWORD)
        cursor = connection.cursor()
        sql = """SELECT * FROM public.order_table"""
        cursor.execute(sql)
        ex = cursor.fetchall()

    except Exception as Error:
        return {"message": str(Error), "status": 1}

    output = {
        "data": dict(ex),
        "tokens": refresh(request.headers.get('refresh_token')),
        "status": 2
    }

    return output



@app.get("/rand_advertisement", tags=["advertisement"])
def get_advertisement():
    connection = connect()
    cursor = connection.cursor()
    try:
        sql = """
                SELECT count(id)
                FROM public.advertisement_table"""
        cursor.execute(sql)
        count = cursor.fetchone()[0]

        number = rand(0, count-1)

        print(id)

        sql = """SELECT json_agg(to_json(row))
                FROM (SELECT *
                FROM public.advertisement_table) row"""

        cursor.execute(sql, (id,))
        ads = cursor.fetchone()[0]
        print(ads[number])

        output_json = {
            "data": ads[number],
            "status": 0
        }

    except Exception as error:
        output_json = {
            "message": str(error),
            "status": 1
        }
    finally:
        connection.commit()
        cursor.close()
        connection.close()

    return output_json


@app.get("/advertisement", tags=["advertisement"])
def get_advertisements():
    connection = connect()
    cursor = connection.cursor()
    try:

        sql = """SELECT json_agg(to_json(row))
                FROM (SELECT *
                FROM public.advertisement_table) row"""

        cursor.execute(sql, (id,))
        ads = cursor.fetchone()[0]


        output_json = {
            "data": ads,
            "status": 0
        }

    except Exception as error:
        output_json = {
            "message": str(error),
            "status": 1
        }
    finally:
        connection.commit()
        cursor.close()
        connection.close()

    return output_json


@app.post("/advertisement", tags=["advertisement"])
def create_advertisement(ad: AdvertisementSchema):
    connection = connect()
    cursor = connection.cursor()
    try:
        sql = """INSERT INTO public.advertisement_table(text)
                 values
                 (%s)"""

        cursor.execute(sql, (ad.text,))
        
        output_json = {
            "message": "Advertisement added",
            "status": 2
        }
    except Exception as error:
        output_json = {
            "message": str(error),
            "status": 1
        }
    finally:
        connection.commit()
        cursor.close()
        connection.close()
    
    return output_json


@app.get("/comment", tags=["comment"])
def get_comment():
    connection = connect()
    cursor = connection.cursor()
    try:
        sql = """SELECT json_agg(to_json(row))
                 FROM (SELECT *
                 FROM public.comment_table) row"""

        cursor.execute(sql)
        ex = cursor.fetchone()[0]
        
        print(ex)

        sql = """SELECT json_agg(to_json(row))
                 FROM (SELECT *
                 FROM public.user_table) row"""

        cursor.execute(sql)
        users = cursor.fetchone()[0]
        # print(user)
        for index, comment in enumerate(ex):
            for user in users:
                if comment['id_user'] == user['id']:
                    ex[index]['user'] = user
                    break
            ex[index].pop('id_user')
        

        # ex['user'] = user

        print(ex)

        output_json = {
            "data": ex,
            "status": 0
        }
    except Exception as error:
        output_json = {
            "message": str(error),
            "status": 1
        }
    finally:
        connection.commit()
        cursor.close()
        connection.close()
    
    return output_json

@app.post("/comment", tags=["comment"])
def create_comment(comment: CommectSchema):
    connection = connect()
    cursor = connection.cursor()
    try:
        sql = """INSERT INTO public.comment_table(text, id_user)
                 values
                 (%s, %s)"""
        cursor.execute(sql, (comment.text,comment.user_id))
        
        output_json = {
            "message": "Advertisement added",
            "status": 2
        }
    except Exception as error:
        output_json = {
            "message": str(error),
            "status": 1
        }
    finally:
        connection.commit()
        cursor.close()
        connection.close()
    
    return output_json


@app.get("/search_products", tags=["products"])
def get_products(name: str):
    connection = connect()
    cursor = connection.cursor()
    try:
        sql = """select upt.id_user, array_agg(upt.id_product)
                from user_products_table upt
                group by upt.id_user"""
        cursor.execute(sql)
        ex = cursor.fetchall()

        sql = """select array_agg(pt.id)
from user_products_table upt
inner join product_table pt on upt.id_product = pt.id
where pt.name = any(array['пушка', 'вульва'])

"""

        cursor.execute(sql)
        arr = cursor.fetchone()[0]

        print(arr)
        print(ex)

        tmp = []

        for index_e, row in enumerate(ex):
            # print(row[1])
            # print(len(row[1]))
            for index, product in enumerate(row[1]):
                # print(product)
                # print(row[1][index])
                if product in arr:
                    tmp.append(product)
            s = list(row)
            s[1] = tmp.copy()
            tmp = []
            ex[index_e] = tuple(s)

        print(1)

        for index in range(len(ex)):
            sql = """select to_json(row)
                     from (
                         select *
                         from public.user_table
                         where id = %s
                     ) row
                     """

            cursor.execute(sql, (ex[index][0],))
            user = cursor.fetchone()[0]
            products = []

            for index_v in range(len(ex[index][1])):
                print(ex[index][1][index_v])
                sql = """select to_json(row)
                     from (
                         select *
                         from public.product_table
                         where id = %s
                     ) row
                     """
                cursor.execute(sql, (ex[index][1][index_v],))
                product = cursor.fetchone()[0]
                print(product)

                sql = """select to_json(row)
                     from (
                         select *
                         from public.category_table
                         where id = %s
                     ) row
                     """

                cursor.execute(sql, (product['category'],))
                category = cursor.fetchone()[0]
                print(category)
                products.append(product)
            

            # print(user)
            tmp = list(ex[index])
            # print(tmp)
            tmp[0] = user
            tmp[1] = products
            ex[index] = tuple(tmp)


        print(ex)
            
        

    except Exception as error:
        return str(error)
    finally:
        cursor.close()
        connection.close()


@app.get("/orders", tags=["orders"])
def get_orders():
    connection = connect()
    cursor = connection.cursor()
    try:
        sql = """SELECT json_agg(to_json(row))
                 FROM (SELECT *
                 FROM order_table) row"""
        cursor.execute(sql)
        orders = cursor.fetchone()[0]

        print(orders)

        for order in orders:
            sql = """SELECT to_json(row)
                    FROM (SELECT *
                    FROM transaction_table
                    WHERE id=%s) row"""
            cursor.execute(sql, (order['id_transaction'],))
            transaction = cursor.fetchone()[0]
            # print(transaction)

            sql = """SELECT to_json(row)
                    FROM (SELECT *
                    FROM user_table
                    WHERE id=%s
                    ) row"""

            cursor.execute(sql, (transaction["id_user_from"],))
            user_from = cursor.fetchone()[0]
            cursor.execute(sql, (transaction["id_user_to"],))
            user_to = cursor.fetchone()[0]

            transaction['user_from'] = user_from
            transaction['user_to'] = user_to
            transaction.pop("id_user_from")
            transaction.pop("id_user_to")

            order["transaction"] = transaction
            order.pop("id_transaction")

            sql = """SELECT json_agg(to_json(row))
                     FROM (SELECT *
                     FROM order_items_table
                     WHERE id_order=%s) row"""

            cursor.execute(sql, (order["id"],))
            items = cursor.fetchone()[0]

            
            for item in items:
                sql = """SELECT to_json(row)
                     FROM (
                         SELECT *
                         FROM product_table
                         WHERE id=%s
                     ) row"""
                cursor.execute(sql, (item["id_product"],))
                product = cursor.fetchone()[0]

                print(product)

                sql = """SELECT to_json(row)
                     FROM (
                         SELECT *
                         FROM category_table
                         WHERE id=%s
                     ) row"""
                print(1)
                cursor.execute(sql, (product["category"],))
                category = cursor.fetchone()[0]
                product["category"] = category

                item["product"] = product
                item["total_price"] = product['price']*item['count']
                item.pop('id_product')
            
            order["items"] = items
            print(items)

        print(orders)

        # print(orders)



    except Exception as error:
        return {"message": str(error), "status": 1}
    finally:
        connection.commit()
        cursor.close()
        connection.close()
    
    return {"data": orders, "status": 0}


@app.put("/products", tags=["products"])
def update_product( image: UploadFile = File(...)):
    connection = connect()
    cursor = connection.cursor()
    try:
        # print("id",id)

        result = uploader.upload(image.file)
        url = result.get('url')
        
        # print("id",id)
        # print(url)

        # sql = """UPDATE product_table 
        #          set
        #          image = %s
        #          where id=%s"""
        # cursor.execute(sql, (url, id))
    except Exception as error:
        return {"message": str(error), "status": 1}
    finally:
        connection.commit()
        cursor.close()
        connection.close()
    return {"message": "Image link to product", "status": 2}
# # db = SessionLocal()

# @app.get("/categories", tags=["categories"], response_model=List[Category], status_code=200)
# def get_categories():
#     with session() as s:
#         categories = s.scalars(select(Category))
#     return categories
