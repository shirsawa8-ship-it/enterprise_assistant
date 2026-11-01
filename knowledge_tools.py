import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.tools import tool
from search_knowledge import search_knowledge


load_dotenv(Path(__file__).resolve().parent / ".env")


@tool
def search_company_policy(question: str)-> dict:
    """检索公司的报销、差旅、考勤等制度，返回参考资料。
    不用于查询某一笔报销申请的金额或处理状态。
    """
    question = question.strip()

    if not question:
        return {
            "sources": [],
            "message": "问题为空。",
        }
    docs = search_knowledge(question, k = 3)

    return {
        "sources": [
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", "未知来源"),
                "chunk_index": doc.metadata.get("chunk_index"),
            }
            for doc in docs
        ]
    }

if __name__ == "__main__":
    result = search_company_policy.invoke("去上海出差最多报销多少")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(search_company_policy.invoke("    "))