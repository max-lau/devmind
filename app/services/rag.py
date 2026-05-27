import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

load_dotenv()

CHROMA_DIR = "chroma_db"
COLLECTION  = "devmind_codebase"

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.getenv("OPENAI_API_KEY")
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1,
    api_key=os.getenv("OPENAI_API_KEY")
)

def load_python_files(root: str = ".") -> list[Document]:
    docs = []
    skip = {".venv", "__pycache__", ".git", "chroma_db"}
    for path in Path(root).rglob("*.py"):
        if any(part in skip for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if text.strip():
            docs.append(Document(
                page_content=text,
                metadata={"source": str(path)}
            ))
    return docs

def build_index() -> Chroma:
    print("Loading Python files...")
    docs = load_python_files()
    print(f"Found {len(docs)} files")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks")

    print("Building vector store...")
    db = Chroma.from_documents(
        chunks,
        embeddings,
        collection_name=COLLECTION,
        persist_directory=CHROMA_DIR
    )
    print("Index built successfully")
    return db

def load_index() -> Chroma:
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

def query_codebase(question: str, k: int = 4) -> dict:
    db = load_index()
    results = db.similarity_search(question, k=k)

    context = "\n\n---\n\n".join([
        f"File: {doc.metadata['source']}\n{doc.page_content}"
        for doc in results
    ])

    messages = [
        SystemMessage(content="""You are a senior software engineer answering questions about a codebase.
Use only the provided code context to answer. Be specific and reference file names.
If the answer is not in the context, say so clearly."""),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}")
    ]

    response = llm.invoke(messages)
    return {
        "answer": response.content,
        "sources": [doc.metadata["source"] for doc in results]
    }