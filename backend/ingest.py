import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma

# Load environment variables
load_dotenv()

def main():
    print("Loading documents...")
    loader = TextLoader("./data/transport_rules.txt")
    documents = loader.load()

    print("Splitting documents...")
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    print("Initializing embeddings (HuggingFace)...")
    # Using a free open-source embedding model
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("Creating Vector DB...")
    # Save the DB locally to ./chroma_db
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    print("Ingestion complete! Vector DB saved to ./chroma_db")

if __name__ == "__main__":
    main()