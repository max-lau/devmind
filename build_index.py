from app.services.rag import build_index

if __name__ == "__main__":
    build_index()
    print("Done — codebase indexed into chroma_db/")