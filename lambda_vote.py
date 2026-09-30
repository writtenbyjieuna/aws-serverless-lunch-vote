import os
import json
import pymysql

DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = "lunch_vote"

def db_connect():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=3306,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    path = event.get("requestContext", {}).get("http", {}).get("path", "")

    if method == "POST" and path == "/vote":
        body = json.loads(event.get("body") or "{}")
        menu = body.get("menu")
        if not menu:
            return {"statusCode": 400, "body": json.dumps({"message": "menu is required"})}

        conn = db_connect()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO votes (menu) VALUES (%s)", (menu,))
        conn.close()

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"{menu}에 투표했습니다."}, ensure_ascii=False)
        }

    if method == "GET" and path == "/summary":
        conn = db_connect()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT menu, COUNT(*) AS count
                FROM votes
                GROUP BY menu
                ORDER BY count DESC
            """)
            results = cursor.fetchall()
        conn.close()
        return {
            "statusCode": 200,
            "body": json.dumps({"result": results}, ensure_ascii=False)
        }

    if method == "GET" and path == "/menus":
        conn = db_connect()
        with conn.cursor() as cursor:
            cursor.execute("SELECT name FROM menus ORDER BY id")
            results = cursor.fetchall()
        conn.close()
        return {
            "statusCode": 200,
            "body": json.dumps({"menus": results}, ensure_ascii=False)
        }

    return {
        "statusCode": 404,
        "body": json.dumps({"message": "Not found"})
    }
