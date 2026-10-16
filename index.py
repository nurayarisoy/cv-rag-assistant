import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

embedding_model = SentenceTransformer(EMBED_MODEL_NAME)


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    if chunk_size <= chunk_overlap:
        raise ValueError("chunk_size overlap'tan büyük olmalıdır")

    chunks = []
    current_lines = []
    current_length = 0

    for line in (line.strip() for line in text.splitlines()):
        if not line:
            continue

        if current_lines and current_length + len(line) + 1 > chunk_size:
            chunks.append("\n".join(current_lines))
            overlap_line = current_lines[-1]
            if len(overlap_line) <= chunk_overlap and len(overlap_line) + len(line) + 1 <= chunk_size:
                current_lines = [overlap_line]
                current_length = len(overlap_line)
            else:
                current_lines = []
                current_length = 0

        current_lines.append(line)
        current_length += len(line) + (1 if len(current_lines) > 1 else 0)

    if current_lines:
        chunks.append("\n".join(current_lines))

    return chunks


with open("cv.txt", "r", encoding="utf-8") as f:
    text = f.read()

chunks = split_text(text, CHUNK_SIZE, CHUNK_OVERLAP)

if not chunks:
    raise RuntimeError("cv.txt dosyası boş veya okunamıyor.")

print(f"{len(chunks)} adet chunk oluşturuldu.")

embeddings = embedding_model.encode(chunks, convert_to_numpy=True).tolist()

client = chromadb.Client(
    Settings(persist_directory="./db", is_persistent=True)
)

existing_collections = [c.name for c in client.list_collections()]
if "cv_collection" in existing_collections:
    client.delete_collection("cv_collection")

collection = client.get_or_create_collection("cv_collection")
collection.add(
    ids=[f"chunk_{i}" for i in range(len(chunks))],
    documents=chunks,
    embeddings=embeddings,
)

print("Indexleme tamamlandı!")
