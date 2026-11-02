import os
from pathlib import Path
from dotenv import load_dotenv

import pymysql
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver

load_dotenv(Path(__file__).resolve().parent / ".env")

def main():
    # 连接专门保存会话状态的数据库
    with pymysql.connect(
        host = os.getenv("MYSQL_HOST","127.0.0.1"),
        port = int(os.getenv("MYSQL_PORT", "3306")),
        user = os.getenv("MYSQL_USER"),
        password = os.environ["MYSQL_PASSWORD"],
        database = os.environ["MYSQL_MEMORY_DATABASE"],
        charset = "utf8mb4",
        autocommit = True,
        connect_timeout = 5,
    )as connection:
        # 将数据库连接交给检查点保存器
        checkpointer = PyMySQLSaver(connection)

        # 创建检查点所需的表
        checkpointer.setup()
        print("会话检查点表初始化完成！")

if __name__ == "__main__":
    main()