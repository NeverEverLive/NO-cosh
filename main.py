from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from core.config import settings
from api.general_pages.home_page import general_pages_router
from api.auth.auth_view import auth_view
from api.comments.comment_view import comment_view
from api.contents.content_view import content_view
from api.advertisement.ads_view import advertisement_view
from api.orders.order_view import order_view
from api.products.product_view import product_view
from api.user.user_view import user_view


def include_router(app):
    app.include_router(general_pages_router)
    app.include_router(auth_view)
    app.include_router(comment_view)
    app.include_router(advertisement_view)
    app.include_router(order_view)
    app.include_router(product_view)
    app.include_router(user_view)
    app.include_router(content_view)


def start_application():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
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
    return app


app = start_application()



'''
# In work
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
'''
