from langchain_core.tools import tool
from expense_repostitory import query_expense, insert_expense
from langgraph.types import interrupt
from langgraph.prebuilt import ToolRuntime

from uuid import NAMESPACE_URL, uuid5

@tool
def get_expense_status(application_id : str) -> dict:
    """根据报销申请编号查询金额和处理状态，例如 BX2026001。不用于查询报销制度。"""
    application_id = application_id.upper().strip()
    if not application_id:
       return {
           "application_id": application_id,
           "found": False,
           "message": "申请编号不能为空！"
            }
    records = query_expense(application_id)
    if records is None:
       return {
           "application_id": application_id,
           "found": False,
           "message": "未找到申请，请核对编号！"
       }
    return {
       "application_id": records["application_id"],
       "found": True,
       "amount": str(records["amount"]),
       "status": records["status"],
   }

@tool
def request_expense_approval(
        applicant_id : str,
        amount : str,
        purpose: str,
        runtime: ToolRuntime,
)-> dict:
    """提交一笔新报销申请，等待人工审核，同意后写入数据库。

    仅在用户明确要求新增报销申请时调用。
    applicant_id 是申请人工号，amount 是金额数字字符串，purpose 是报销用途。
    报销申请编号由工具自动生成，无需用户提供。
    人工同意后返回 approved=True 和申请编号；拒绝返回 approved=False，不创建记录。
    提交成功不代表财务审核完成或已经付款。
    """
    thread_id = runtime.config["configurable"]["thread_id"]
    application_id = "BX" + uuid5(
        NAMESPACE_URL,
        f"{thread_id}: {runtime.tool_call_id}",
    ).hex.upper()

    draft = {
        "application_id": application_id,
        "applicant_id": applicant_id,
        "amount": amount,
        "purpose": purpose,
    }

    approved = interrupt({
        "action": "submit_expense",
        "draft": draft,
    })
    if approved is not True:
        return {
            "application_id": application_id,
            "draft": draft,
            "approved": False,
        }
    insert_expense(
        application_id = application_id,
        applicant_id = applicant_id,
        amount = amount,
        purpose = purpose,
    )
    return {
        "applicant_id": applicant_id,
        "application_id": application_id,
        "approved": True,
        "draft": draft,
    }

if __name__ == "__main__":
    docs = [
        {"application_id": "BX2026001"},
        {"application_id": " bx2026002 "},
        {"application_id": "BX9999999"}
    ]
    for doc in docs:
        result = get_expense_status.invoke(doc)
        print(result)