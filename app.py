import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from transformers import pipeline

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
QA_MODEL_NAME = "google/flan-t5-small"

embedding_model = SentenceTransformer(EMBED_MODEL_NAME)
qa_model = pipeline(
    "text2text-generation",
    model=QA_MODEL_NAME,
    device=-1,
    max_length=256,
    do_sample=False,
)

client = chromadb.Client(
    Settings(persist_directory="./db", is_persistent=True)
)

try:
    collection = client.get_collection("cv_collection")
except Exception as exc:
    raise RuntimeError(
        "cv koleksiyonu bulunamadı. Önce index.py'yi çalıştırarak veritabanını oluşturun."
    ) from exc


def embed_query(text: str) -> list[float]:
    return embedding_model.encode(text, convert_to_numpy=True).tolist()


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
Kontext:
{context}

Soru:
{question}

Cevabı açık ve kısa ver.
"""

    response = qa_model(prompt, truncation=True)[0]["generated_text"]
    print("\nAnswer:\n", response)
