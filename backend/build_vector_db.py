import os
import glob
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables (for GEMINI_API_KEY)
load_dotenv()

def build_db():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    persist_dir = os.path.join(data_dir, "chroma_db")
    
    print("Loading documents...")
    # Read all markdown files from data/
    docs_texts = []
    metadata = []
    
    for domain in ["hackerrank", "claude", "visa"]:
        filepath = os.path.join(data_dir, domain, "corpus.md")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                docs_texts.append(content)
                metadata.append({"domain": domain, "source": filepath})
    
    if not docs_texts:
        print("No documents found in data directory.")
        return

    print("Splitting texts...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    split_docs = text_splitter.create_documents(docs_texts, metadatas=metadata)
    print(f"Created {len(split_docs)} document chunks.")

    print("Initializing embeddings model...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    print("Building and persisting vector database...")
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    
    print(f"Vector DB successfully created at: {persist_dir}")

if __name__ == "__main__":
    build_db()
