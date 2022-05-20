# main:app --reload
from typing import List
from core.config import settings
from fastapi import Body, FastAPI, Depends
from api.general_pages.home_page import general_pages_router
# from db.session import connect
# from db.base_class import Base
# from db.session import engine, SessionLocal
# from model import Category, OrderSchema, UserSchema, UserLoginSchema
# from api.auth.jwt_handler import signJWT
# from api.auth.jwt_bearer import jwtBearer
# from db.session import session
# from sqlalchemy import select

def include_router(app):
    app.include_router(general_pages_router)

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
    # create_tables()
    return app




app = start_application()

# @app.get("/orders", tags=['orders'])
# def get_orders():
#     return {"data": orders, "status": 0}


# @app.get("/orders/{id}", tags=['orders'])
# def get_order(id: int):
#     if id > len(orders):
#         return {
#             "error": "Order with this id does not exist"
#         }
#     for order in orders:
#         if order["id"] == id:
#             return {
#                 "data": order
#             }


# @app.post("/orders", dependencies=[Depends(jwtBearer())], tags=['orders'])
# def add_order(order: OrderSchema):
#     order.id = len(orders) + 1
#     orders.append(order.dict())
#     return {
#         "message": "Order created"
#     }


# @app.post("/users/signup", tags=["users"])
# def user_signup(user: UserSchema = Body(default=None)):
#     users.append(user)
#     return signJWT(user.email)


# # @app.post("/users/signup", tags=["users"])
# def check_user(data: UserLoginSchema):
#     # добавить проверку на то что токен не в blacklist'е
#     for user in users:
#         if user.email == data.email and user.password == data.password:
#             return True
#         return False



# @app.post("/users/login", tags=["users"])
# def user_login(user: UserLoginSchema = Body(default=None)):
#     if check_user(user):
#         return signJWT(user.email)
#     else:
#         return {
#             "error": "Invalid login details"
#         }


# @app.post("users/logout", tags=["users"])
# def user_logout(user: UserLoginSchema = Body(default=None)):
#     # Добавить токен в блэклист
#     pass


# # db = SessionLocal()

# @app.get("/categories", tags=["categories"], response_model=List[Category], status_code=200)
# def get_categories():
#     with session() as s:
#         categories = s.scalars(select(Category))
#     return categories
