import os
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from core import config


def main():
    print("Loading documents...")
    rules_path = os.path.join(config.DATA_DIR, "transport_rules.txt")
    loader = TextLoader(rules_path)
    documents = loader.load()

    print("Splitting documents...")
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    print("Initializing embeddings (HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("Creating Vector DB...")
    Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=config.CHROMA_DB_DIR,
    )

    print("Ingestion complete! Vector DB saved to ./chroma_db")


if __name__ == "__main__":
    main()
