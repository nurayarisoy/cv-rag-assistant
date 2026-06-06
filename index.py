import os
from pathlib import Path

import openai
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY bulunamadı. Lütfen .env dosyası veya ortam değişkeni olarak ayarlayın."
    )
openai.api_key = OPENAI_API_KEY

CHUNK_SIZE = 300
CHUNK_OVERLAP = 50


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    if chunk_size <= chunk_overlap:
        raise ValueError("chunk_size overlap'tan büyük olmalıdır")

    chunks = []
    start = 0
    text = text.strip()

    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start += chunk_size - chunk_overlap

    return chunks


with open("cv.txt", "r", encoding="utf-8") as f:
    text = f.read()

chunks = split_text(text, CHUNK_SIZE, CHUNK_OVERLAP)

if not chunks:
    raise RuntimeError("cv.txt dosyası boş veya okunamıyor.")

print(f"{len(chunks)} adet chunk oluşturuldu.")

response = openai.Embedding.create(
    model="text-embedding-3-small",
    input=chunks,
)
embeddings = [item["embedding"] for item in response["data"]]

client = chromadb.Client(
    Settings(persist_directory="./db", is_persistent=True)
)

existing_collections = [c.name for c in client.list_collections()]
if "cv" in existing_collections:
    client.delete_collection("cv")

collection = client.get_or_create_collection("cv")
collection.add(
    ids=[f"chunk_{i}" for i in range(len(chunks))],
    documents=chunks,
    embeddings=embeddings,
)

print("Indexleme tamamlandı!")

