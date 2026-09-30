import os
import csv
import io
import boto3
import pymysql

DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ["DB_NAME"]

s3 = boto3.client("s3")

def db_connect():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=3306,
        autocommit=True
    )

def lambda_handler(event, context):
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))

    menus = []
    for row in reader:
        name = row["name"].strip()
        if name:
            menus.append(name)

    conn = db_connect()
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menus (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            )
        """)
        cursor.execute("DELETE FROM menus")
        for menu in menus:
            cursor.execute("INSERT INTO menus (name) VALUES (%s)", (menu,))
    conn.close()

    return {
        "statusCode": 200,
        "body": f"{len(menus)} menus synced"
    }
