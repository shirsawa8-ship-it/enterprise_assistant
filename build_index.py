from langchain_ollama import OllamaEmbeddings
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

def split_knowledge(
        text: str,
        chunk_size: int = 400,
        chunk_overlap: int = 80,
          ) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        separators = ["\n\n", "\n","\t", "。", "，", " ", ""],
    )
    chunks = splitter.split_text(text)
    return chunks

KNOWLEDGE_PATH = Path(__file__).resolve().parent / "knowledge.txt"
CHROMA_PATH = KNOWLEDGE_PATH.parent / "chroma_db"


def main():
    knowledge = KNOWLEDGE_PATH.read_text(encoding="utf-8")
    chunks = split_knowledge(knowledge)

    embeddings = OllamaEmbeddings(
        base_url = "http://127.0.0.1:11434",
        model = "bge-m3",
    )
    vector_store = Chroma(
        collection_name = "company_knowledge",
        embedding_function = embeddings,
        persist_directory = str(CHROMA_PATH),
    )
    existing = vector_store.get(limit = 1)
    if existing["ids"]:
        print("已有资料")
        return
    if not chunks:
        print("资料为空，没有内容可入库。")
        return
    vector_store.add_texts(
        texts = chunks,
        metadatas = [
            {"source" : "knowledge.txt","chunk_index" : index}
            for index in range(len(chunks))
        ],
        ids = [f"knowledge--{index}"for index in range(len(chunks))]
        )
    print(f"入库完成：共{len(chunks)}个片段")

if __name__ == "__main__":
    main()