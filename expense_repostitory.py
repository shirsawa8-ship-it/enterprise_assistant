import os
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent / ".env")

def query_expense(application_id: str) -> dict | None:
    """根据申请编号查询一条报销记录。"""
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        charset="utf8mb4",
        connection_timeout=5,
    )

    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)

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


if __name__ == "__main__":
    print(query_expense(""))
    print(query_expense("    "))
    print(query_expense("BX2026001"))
    print(query_expense("BX2026002"))
    print(query_expense("BX2026003"))