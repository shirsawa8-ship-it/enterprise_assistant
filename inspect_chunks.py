from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter


def main():
    KNOWLEDGE_PATH = Path(__file__).resolve().parent / "knowledge.txt"
    text = KNOWLEDGE_PATH.read_text(encoding="utf-8")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 400,
        chunk_overlap = 80,
        separators = ["\n\n", "\n","\t", "。", "，", " ", ""],
    )
    chunks = splitter.split_text(text)

    for index, chunk in enumerate(chunks, start=1):
        print(f"\n--- 第 {index} 块，长度 {len(chunk)} ---")
        print(chunk)

if __name__ == "__main__":
    main()