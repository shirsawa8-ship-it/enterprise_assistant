from pathlib import Path
from dotenv import load_dotenv
from time import perf_counter
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel,Field
from langsmith import traceable

import os
import pymysql
from contextlib import asynccontextmanager
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver
from agent_graph import build_graph

load_dotenv(Path(__file__).resolve().parent / ".env")

class ChatRequest(BaseModel):
    question : str = Field(min_length=1,max_length=2000)
    session_id: str = Field(min_length=1,max_length=64)

@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = pymysql.connect(
        host = os.getenv("MYSQL_HOST", "127.0.0.1"),
        port = int(os.getenv("MYSQL_PORT", 3306)),
        user = os.environ["MYSQL_USER"],
        password = os.environ["MYSQL_PASSWORD"],
        database = os.environ["MYSQL_MEMORY_DATABASE"],
        charset = "utf8mb4",
        autocommit = True,
        connect_timeout = 5,
    )
    try:
        checkpointer = PyMySQLSaver(connection)
        checkpointer.setup()

        app.state.graph = build_graph(checkpointer)
        yield

    finally:
        connection.close()

app = FastAPI(
    title="企业知识库助手",
    lifespan=lifespan,
)

@app.post("/chat")
@traceable(name= "企业知识库问答", run_type= "chain")
def chat(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(
            status_code = 422,
            detail = "问题不能为空！"
        )

    try:
        invoke_time_start = perf_counter()
        response = app.state.graph.invoke(
            {"messages": [("human", request.question.strip())], },
             config = {
             "configurable": {
             "thread_id": request.session_id,
             }
             }
        )
        invoke_time_end = perf_counter()

        answer = response["messages"][-1].content
        if not answer.strip():
            raise HTTPException(
                status_code=502,
                detail="模型未生成答案，请稍后再试"
            )
        return {
            "answer": answer,
            "invoke_time": round(invoke_time_end - invoke_time_start, 3),
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"模型调用失败{type(e).__name__}",flush = True)
        raise HTTPException(
            status_code = 502,
            detail = f"模型调用失败！{type(e).__name__}",
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8888, reload=True)