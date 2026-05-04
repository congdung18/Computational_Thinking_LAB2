from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from core import config

PROMPT_TEMPLATE = """
You are a helpful transportation assistant. Use the following context rules to recommend the best transportation method (walk, bike, motorbike, car, public transportation, etc.) based on the user's weather conditions and preferences.

Context (Rules):
{context}

User's Input:
- Weather conditions: {weather}
- User preferences/Distance: {preferences}

Based on the rules and input, recommend the best transportation method and provide a brief explanation why. If the rules don't cover the exact scenario, make a logical recommendation.

Recommendation:
"""


class RagService:
    def __init__(self):
        self.retriever = None
        self.llm = None
        self.chain = None

        self._init_retriever()
        self._init_chain()

    def _init_retriever(self):
        print("Initializing embeddings and Vector DB connection...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        try:
            vector_store = Chroma(
                persist_directory=config.CHROMA_DB_DIR,
                embedding_function=embeddings,
            )
            self.retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        except Exception as exc:
            print(
                f"Failed to load Chroma DB: {exc}. Make sure to run the ingestion script first."
            )
            self.retriever = None

    def _init_chain(self):
        try:
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
        except Exception as exc:
            print(f"Failed to initialize Gemini: {exc}")
            self.llm = None
            self.chain = None
            return

        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        self.chain = prompt | self.llm | StrOutputParser()

    def retriever_ready(self):
        return self.retriever is not None

    def llm_ready(self):
        return self.llm is not None

    def is_ready(self):
        return self.retriever_ready() and self.llm_ready() and self.chain is not None

    def suggest(self, weather: str, preferences: str):
        if not self.is_ready():
            raise RuntimeError(
                "RAG system is not properly initialized. Check API keys and ensure ingestion was run."
            )

        query = f"Weather: {weather}. Preferences: {preferences}"
        docs = self.retriever.invoke(query)
        context = self._format_docs(docs)
        return self.chain.invoke(
            {"context": context, "weather": weather, "preferences": preferences}
        )

    @staticmethod
    def _format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
