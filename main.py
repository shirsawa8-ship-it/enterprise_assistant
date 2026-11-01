from pathlib import Path
from dotenv import load_dotenv
from time import perf_counter
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel,Field
from langsmith import traceable

from agent_graph import graph

load_dotenv(Path(__file__).resolve().parent / ".env")

class ChatRequest(BaseModel):
    question : str = Field(min_length=1,max_length=2000)
    session_id: str = Field(min_length=1,max_length=32)

app = FastAPI(title= "企业知识库助手")

@app.post("/chat")
@traceable(name= "企业知识库问答", run_type= "chain")
def chat(request: ChatRequest):
    print("1检索开始",flush=True)
    question = request.question.strip()
    if not question:
        raise HTTPException(
            status_code = 422,
            detail = "问题不能为空！"
        )

    try:
        invoke_time_start = perf_counter()
        response = graph.invoke(
            {"messages": [("human", request.question.strip())],},
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