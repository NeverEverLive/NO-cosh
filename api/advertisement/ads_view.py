from fastapi import APIRouter, Body
from random import randint as rand

from db.session import connect
from model import AdvertisementSchema


advertisement_view = APIRouter()


@advertisement_view.get("/rand_advertisement", tags=["advertisement"])
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


@advertisement_view.get("/advertisement", tags=["advertisement"])
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


@advertisement_view.post("/advertisement", tags=["advertisement"])
def create_advertisement(ad: AdvertisementSchema = Body(default=None)):
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
