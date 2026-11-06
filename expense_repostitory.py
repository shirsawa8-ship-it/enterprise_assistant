import os
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent / ".env")

def query_expense(application_id: str) -> dict | None:
    """根据申请编号查询一条报销记录。"""
    connection = mysql.connector.connect(
        host = os.getenv("MYSQL_HOST"),
        port = int(os.getenv("MYSQL_PORT")),
        user = os.getenv("MYSQL_USER"),
        password = os.getenv("MYSQL_PASSWORD"),
        database = os.getenv("MYSQL_DATABASE"),
        charset = "utf8mb4",
        connection_timeout = 5,
    )

    cursor = None
    try:
        cursor = connection.cursor(dictionary = True)

        sql = """
        SELECT application_id, applicant_id, amount, status, created_at, updated_at
        FROM enterprise_assistant
        WHERE application_id = %s
        """
        cursor.execute(sql, (application_id,))
        result = cursor.fetchone()
        return result
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

def insert_expense(
        application_id: str,
        applicant_id: str,
        amount: str,
        purpose: str,
) -> str:
    """新增报销记录，返回申请编号。"""
    connection = mysql.connector.connect(
        host = os.getenv("MYSQL_HOST"),
        port = int(os.getenv("MYSQL_PORT")),
        user = os.getenv("MYSQL_USER"),
        password = os.getenv("MYSQL_PASSWORD"),
        database = os.getenv("MYSQL_DATABASE"),
        charset = "utf8mb4",
        connection_timeout = 5,
    )
    cursor = None
    try:
        cursor = connection.cursor(dictionary = True)

        sql = """
            INSERT INTO enterprise_assistant
                (application_id, applicant_id, amount, purpose, status)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE application_id = application_id
        """
        cursor.execute(
            sql,
            (application_id, applicant_id, amount, purpose, "已提交"),
        )
        connection.commit()
        return application_id
    except mysql.connector.Error:
        connection.rollback()   #回滚未提交的修改
        raise
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

if __name__ == "__main__":
    application_id = insert_expense(
        application_id = "BX_TEST_20261106_001",
        applicant_id = "EMP001",
        amount = "800.00",
        purpose = "上海出差住宿费",
    )

    print("申请编号", application_id)
    print("查询结果", query_expense(application_id))