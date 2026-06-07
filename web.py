from flask import Flask, render_template, request
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
except Exception:
    collection = None


def embed_query(text: str) -> list[float]:
    return embedding_model.encode(text, convert_to_numpy=True).tolist()


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    answer = None
    documents = []
    error = None

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
Kontext:
{context}

Frage:
{query}

Antwort klar und kurz.
"""
                    answer = qa_model(prompt, truncation=True)[0]["generated_text"]
                else:
                    error = "Sonuç bulunamadı."
            except Exception as exc:
                error = str(exc)

    return render_template(
        "index.html",
        query=query,
        answer=answer,
        documents=documents[0] if documents else [],
        error=error,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(__import__('os').getenv("PORT", "5000")), debug=True)
