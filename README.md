---
title: Cv Rag Assistant
emoji: 📚
colorFrom: blue
colorTo: red
sdk: docker
pinned: false
---

# CV RAG Assistant

CV RAG Assistant is a simple RAG application that indexes resume content from `cv.txt` into a vector database and answers user questions. The project works both from the command line and through a Flask-based web interface.

## How It Works

1. `index.py` splits the content of `cv.txt` into chunks.
2. It generates embeddings with the `sentence-transformers/all-MiniLM-L6-v2` model.
3. It writes those embeddings into ChromaDB under the `db/` directory.
4. `app.py` or `web.py` embeds the user's question and retrieves the most relevant chunks.
5. The `google/flan-t5-small` model generates a short answer based on that context.

## Features

- Stores CV data persistently with local ChromaDB.
- Provides both a terminal flow and a web interface.
- Can run with Docker.
- Because indexing is a separate step, you can rebuild the index whenever `cv.txt` changes.

## Requirements

- Python 3.10+
- `pip`
- Internet access for model downloads on first run

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Build the Index

Run the following command after the initial setup or whenever `cv.txt` changes:

```bash
python index.py
```

This command recreates the `cv_collection` collection.

## Run from the Terminal

```bash
python app.py
```

Example question:

```text
Ask: What technical skills does the candidate have?
```

## Web Interface

```bash
python web.py
```

The application runs on `http://localhost:7860` by default.

## Run with Docker

```bash
docker build -t cv-rag-assistant .
docker run --rm -p 7860:7860 cv-rag-assistant
```

The current `Dockerfile` automatically runs `python index.py` during the image build. Because of that, `cv.txt` must be copied into the image.

## Project Structure

```text
.
|-- app.py            # Terminal-based question-answer flow
|-- index.py          # Splits, embeds, and writes CV data to ChromaDB
|-- web.py            # Flask web application
|-- cv.txt            # CV text to be indexed
|-- templates/
|   `-- index.html    # Web interface
`-- db/               # Persistent ChromaDB data
```

## Notes

- `index.py` deletes the existing `cv_collection` collection and recreates it.
- Model downloads may take time during the first run.
- Generated answers depend on the content of `cv.txt` and the retrieved chunks.

## Deployment

See [DEPLOY.md](./DEPLOY.md) for deployment options.
