from dotenv import load_dotenv
from pathlib import Path
from langchain_ollama import ChatOllama
from expense_tools import get_expense_status
import json
from langchain_core.messages import ToolMessage

load_dotenv(Path(__file__).resolve().parent / ".env")

model = ChatOllama(
    base_url = "http://127.0.0.1:11434",
    model = "qwen3:4b",
    temperature = 0,
    reasoning=True,         #思考模式
    num_ctx=4096,           #上下文容量
    num_predict=4096,        #限制生成的 token 数
    client_kwargs={"timeout": 360},     #响应时间上限
)

model_with_tools = model.bind_tools([get_expense_status,])

if __name__ == "__main__":
    question = "查询 BX2026001 和 BX2026002"
    messages = [
        (
            "system",
            "你是企业报销助手。"
            "查询具体报销申请的状态时，使用报销状态查询工具"
            "缺少申请编号时，先询问用户，不要自行编造编号。"
            "报销制度问题不使用状态查询工具。"
            "如果检测到用户输入的编号有误，主动提醒用户"
            "尚未获得工具结果时，不要编造申请金额或状态。",
        ),
        ("human", question),
    ]
    result = model_with_tools.invoke(messages)

    print("文本回答：\n",result.content_blocks)
    print("工具调用：\n",result.tool_calls)
    if result.tool_calls:
        messages.append(result)

        tools_by_name = {
            get_expense_status.name: get_expense_status,
        }

        for tool_call in result.tool_calls:
            tool_name = tool_call["name"]
            if tool_name not in tools_by_name:
                raise ValueError(f"未知工具{tool_name}")
            selected_tool = tools_by_name[tool_name]
            result_tool_call = selected_tool.invoke(tool_call["args"])

            print(f"使用工具：{tool_name}")
            print(f"工具使用结果：{result_tool_call}")

            messages.append(
                ToolMessage(
                    content = json.dumps(result_tool_call, ensure_ascii=False),     #ensure_ascii使中文保持可读
                    tool_call_id = tool_call["id"]
                )
            )
            final_response = model.invoke(messages)
        print(f"最终回答：{final_response.content}")
    else:
        print(f"直接回答：{result.content}")