import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template, request
import openai
import chromadb
from chromadb.config import Settings
from langchain_openai import ChatOpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY bulunamadı. Lütfen .env dosyası veya ortam değişkeni olarak ayarlayın."
    )
openai.api_key = OPENAI_API_KEY

client = chromadb.Client(
    Settings(persist_directory="./db", is_persistent=True)
)

try:
    collection = client.get_collection("cv")
except Exception:
    collection = None

llm = ChatOpenAI(model="gpt-4o-mini")


def embed_query(text: str) -> list[float]:
    response = openai.Embedding.create(
        model="text-embedding-3-small",
        input=[text],
    )
    return response["data"][0]["embedding"]


def load_resume_text() -> str:
    path = Path("cv.txt")
    return path.read_text(encoding="utf-8") if path.exists() else "CV dosyası bulunamadı."


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    answer = None
    documents = []
    error = None
    resume_text = load_resume_text()

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if not query:
            error = "Lütfen bir arama terimi girin."
        elif collection is None:
            error = "cv koleksiyonu bulunamadı. Önce index.py'yi çalıştırın."
        else:
            try:
                query_embedding = embed_query(query)
                result = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=3,
                    include=["documents"],
                )
                documents = result.get("documents", [])
                if documents and documents[0]:
                    context = "\n".join(documents[0])
                    prompt = f"""
You are a CV assistant.

Context:
{context}

Question:
{query}

Answer clearly and concisely.
"""
                    response = llm.invoke(prompt)
                    answer = response.content
                else:
                    error = "Sonuç bulunamadı."
            except Exception as exc:
                error = str(exc)

    return render_template(
        "index.html",
        query=query,
        answer=answer,
        documents=documents[0] if documents else [],
        resume_text=resume_text,
        error=error,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
