
import os
from pathlib import Path

import openai
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
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
except Exception as exc:
    raise RuntimeError(
        "cv koleksiyonu bulunamadı. Önce index.py'yi çalıştırarak veritabanını oluşturun."
    ) from exc

llm = ChatOpenAI(model="gpt-4o-mini")


def embed_query(text: str) -> list[float]:
    response = openai.Embedding.create(
        model="text-embedding-3-small",
        input=[text],
    )
    return response["data"][0]["embedding"]


while True:
    question = input("Ask: ")
    if not question.strip():
        print("Lütfen bir soru yazın.")
        continue

    query_embedding = embed_query(question)
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents"],
    )

    documents = result.get("documents", [])
    if not documents or not documents[0]:
        print("Sonuç bulunamadı.")
        continue

    context = "\n".join(documents[0])

    prompt = f"""
You are a CV assistant.

Context:
{context}

Question:
{question}

Answer clearly and concisely.
"""

    response = llm.invoke(prompt)
    print("\nAnswer:", response.content)
