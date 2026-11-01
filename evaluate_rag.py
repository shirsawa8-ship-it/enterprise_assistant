from pathlib import Path

import httpx
from dotenv import load_dotenv
from langsmith import Client

from uuid import uuid4

load_dotenv(Path(__file__).resolve().parent / ".env")


def predict(inputs: dict) -> dict:
    question = inputs["input"]
    print(f"正在测试：{question}", flush=True)

    response = httpx.post(
        "http://127.0.0.1:8888/chat",
        json={
            "question": question,
            "session_id": uuid4().hex,
        },
        timeout=360,
    )
    response.raise_for_status()         #检查响应状态

    result = response.json()

    return {
        "output": result["answer"],
        "invoke_time": result["invoke_time"],
    }


if __name__ == "__main__":
    client = Client()

    client.evaluate(
        predict,
        data="enterprise-rag-basic-v1",
        experiment_prefix="qwen3-4b-baseline",
        max_concurrency=1,
    )

    print("实验执行结束，请到 LangSmith 检查结果。", flush=True)