from fastapi import APIRouter

from db.session import connect
from model import CommectSchema


comment_view = APIRouter()


@comment_view.get("/comment", tags=["comment"])
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

@comment_view.post("/comment", tags=["comment"])
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
