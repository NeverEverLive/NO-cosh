from fastapi import APIRouter

from db.session import connect


order_view = APIRouter()


@order_view.get("/orders", tags=["orders"])
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
            print(transaction)

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
            print(transaction)

            order["transaction"] = transaction
            order.pop("id_transaction")

            print(order)

            sql = """SELECT json_agg(to_json(row))
                     FROM (SELECT *
                     FROM order_items_table
                     WHERE id_order=%s) row"""

            cursor.execute(sql, (order["id"],))
            items = cursor.fetchone()[0]

            print(items)

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
