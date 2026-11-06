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
from langgraph.types import Command

load_dotenv(Path(__file__).resolve().parent / ".env")

class ChatRequest(BaseModel):
    question : str = Field(min_length=1,max_length=2000)
    session_id: str = Field(min_length=1,max_length=64)
class ApprovalRequest(BaseModel):
    session_id: str = Field(min_length=1,max_length=64)
    approval_id: str
    approved: bool

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

        if response.get("__interrupt__"):
            return {
                "status": "pending_approval",
                "session_id": request.session_id,
                "approval_requests": [
                    {
                        "id": item.id,
                        "data": item.value,
                    }
                    for item in response["__interrupt__"]
                ],
                "invoke_time": round(invoke_time_end - invoke_time_start, 2),
            }

        answer = response["messages"][-1].content
        if not answer.strip():
            raise HTTPException(
                status_code = 502,
                detail = "模型未生成答案，请稍后再试"
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
@app.post("/approval")
def approval(request: ApprovalRequest):
    config = {
        "configurable": {
            "thread_id": request.session_id,
        }
    }
    snapshot = app.state.graph.get_state(config = config)
    pending_ids = []
    for task in snapshot.tasks:
        for item in task.interrupts:
            pending_ids.append(item.id)
    if request.approval_id not in pending_ids:
        raise HTTPException(
            status_code = 409,
            detail = "该会话中没有这项审核申请，请检查会话和审核编号"
        )

    response = app.state.graph.invoke(
        Command(
            resume = {request.approval_id: request.approved},
        ),
        config,
    )
    if response.get("__interrupt__"):
        return {
            "status": "pending_approval",
            "session_id": request.session_id,
            "approval_requests": [
                {
                    "id": item.id,
                    "data": item.value
                }for item in response["__interrupt__"]
            ]
        }
    answer = response["messages"][-1].content
    if not answer.strip():
        raise HTTPException(
            status_code = 502,
            detail = "模型未生成审核结果说明！"
        )
    return {
        "status": "completed",
        "session_id": request.session_id,
        "approved": request.approved,
        "answer": answer,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8888, reload=True)