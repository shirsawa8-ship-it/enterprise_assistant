from langchain_core.tools import tool
from expense_repostitory import query_expense


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

if __name__ == "__main__":
    docs = [
        {"application_id": "BX2026001"},
        {"application_id": " bx2026002 "},
        {"application_id": "BX9999999"}
    ]
    for doc in docs:
        result = get_expense_status.invoke(doc)
        print(result)