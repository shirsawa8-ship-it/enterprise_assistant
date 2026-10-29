import pathlib
from langsmith import traceable
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

CHROMA_PATH = pathlib.Path(__file__).resolve().parent / "chroma_db"

bge_m3_embeddings = OllamaEmbeddings(
    model = "bge-m3",
    base_url = "http://127.0.0.1:11434",
    client_kwargs = {"timeout": 40},
)

vector_store = Chroma(
    collection_name= "company_knowledge",
    embedding_function= bge_m3_embeddings,
    persist_directory= str(CHROMA_PATH),
)
@traceable(name= "知识库检索", run_type= "retriever")
def search_knowledge(question: str , k: int = 3):
    return vector_store.similarity_search(question, k)

if __name__ == "__main__":
    result = search_knowledge("去上海出差，报销上限是多少？",2)

    for index,doc in enumerate(result , start = 1):
        print(f"\n检索结果：{index}")
        print("来源：", doc.metadata)
        print("结果：", doc.page_content)