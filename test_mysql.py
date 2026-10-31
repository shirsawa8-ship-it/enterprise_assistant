import os
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector

load_dotenv(Path(__file__).resolve().parent / ".env")

connection = mysql.connector.connect(
    host = os.getenv("MYSQL_HOST"),
    user = os.getenv("MYSQL_USER"),
    port = int(os.getenv("MYSQL_PORT", "3306")),
    password = os.getenv("MYSQL_PASSWORD"),
    database = os.getenv("MYSQL_DATABASE"),
    charset = "utf8mb4",
    connection_timeout = 5,
)
cursor = None
try:
    cursor = connection.cursor(dictionary= True)

    sql = """
        SELECT application_id, applicant_id, amount, status
        FROM enterprise_assistant
        WHERE application_id = %s
    """
    cursor.execute(sql, ("BX2026001",))
    record = cursor.fetchone()
    print("查询结果：",record)
finally:
    if cursor is not None:
        cursor.close()
    connection.close()
    print("连接已关闭")