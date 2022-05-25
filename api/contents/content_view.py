from fastapi import APIRouter, UploadFile, File, Body
from cloudinary import uploader
import cloudinary
from datetime import datetime

from db.session import connect


content_view = APIRouter()


@content_view.get("/content", tags=["content"])
def get_content():
    connection = connect()
    cursor = connection.cursor()
    try:

        sql = """SELECT json_agg(to_json(row))
                FROM (SELECT *
                FROM public.content_table) row"""

        cursor.execute(sql)
        ex = cursor.fetchone()[0]

        output_json = {
            "data": ex,
            "status": 0
        }
    except Exception as error:
        return {"message": str(error), "status": 1}
    finally:
        connection.commit()
        cursor.close()
        connection.close()
    return output_json

@content_view.get("/content/{id}", tags=["content"])
def get_content(id: int):
    connection = connect()
    cursor = connection.cursor()
    try:

        sql = """SELECT json_agg(to_json(row))
                FROM (SELECT *
                FROM public.content_table
                where id=%s) row"""

        cursor.execute(sql, (id,))
        ex = cursor.fetchone()[0]

        output_json = {
            "data": ex,
            "status": 0
        }
    except Exception as error:
        return {"message": str(error), "status": 1}
    finally:
        connection.commit()
        cursor.close()
        connection.close()
    return output_json


@content_view.post("/content", tags=["content"])
def create_content(text: str = Body(default=None), image: UploadFile = File(...)):
    connection = connect()
    cursor = connection.cursor()
    try:

        result = uploader.upload(image.file)
        url = result.get('url')

        sql = """INSERT INTO content_table(text, image, date)
                 values
                 (%s, %s, %s)"""
        
        cursor.execute(sql, (text, url, str(datetime.today())))
    except Exception as error:
        return {"message": str(error), "status": 1}
    finally:
        connection.commit()
        cursor.close()
        connection.close()
    return {"message": "Content created", "status": 2}
