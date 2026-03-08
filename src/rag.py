from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

def init_rag():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    if Path("prd_vectorstore").exists():
        return FAISS.load_local(
            "prd_vectorstore",
            embeddings,
            allow_dangerous_deserialization=True,
        )

    loader = TextLoader("PRD.md")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    chunks = splitter.split_documents(docs)

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local("prd_vectorstore")

    return vectorstore

def get_rag_advice(state):
    vectorstore = init_rag()

    docs = vectorstore.similarity_search(
        "speech dataset quality rules",
        k=2,
    )

    return "\n".join([d.page_content for d in docs])