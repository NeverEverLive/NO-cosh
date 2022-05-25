from fastapi import APIRouter, UploadFile, File
from cloudinary import uploader
import cloudinary

from db.session import connect


product_view = APIRouter()


@product_view.put("/products/{id}", tags=["products"])
def update_product(id:int, image: UploadFile = File(...)):
    connection = connect()
    cursor = connection.cursor()
    try:
        print("id", id)

        result = uploader.upload(image.file)
        url = result.get('url')
        
        # print("id",id)
        # print(url)

        sql = """UPDATE product_table 
                 set
                 image = %s
                 where id=%s"""
        cursor.execute(sql, (url, id))
    except Exception as error:
        return {"message": str(error), "status": 1}
    finally:
        connection.commit()
        cursor.close()
        connection.close()
    return {"message": "Image link to product", "status": 2}
