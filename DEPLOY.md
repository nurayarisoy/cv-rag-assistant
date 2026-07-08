# Deployment Guide

This project can run on Heroku, VPS providers, or any platform that supports Docker.

## Heroku

The application is ready for Heroku-style runtime behavior:

- `Procfile` starts the app with `gunicorn`
- `web.py` reads the `PORT` environment variable
- `GET /health` is available for smoke checks

### Deploy with Git

```bash
heroku create <your-app-name>
git push heroku main
```

After deployment, open:

```bash
heroku open
```

Your app URL will be:

```text
https://<your-app-name>.herokuapp.com
```

### Useful Heroku Commands

```bash
heroku logs --tail
heroku ps
heroku apps:info
curl https://<your-app-name>.herokuapp.com/health
```

## Docker Image via GitHub Container Registry

The repository already includes a GitHub Actions workflow that builds and pushes an image to `ghcr.io` on every push to `main`.

Published image:

```text
ghcr.io/<owner>/<repo>:latest
```

## Run on a VPS

Pull from GHCR:

```bash
docker run -d -p 7860:7860 ghcr.io/<owner>/<repo>:latest
```

Or build on the server:

```bash
docker build -t cv-rag-assistant:latest .
docker run -d -p 7860:7860 cv-rag-assistant:latest
```

Health check:

```bash
curl http://localhost:7860/health
```

## Render or Railway

- Connect the repository and deploy with the existing `Dockerfile`, or use the GHCR image directly.
- Be aware that model downloads can make cold starts slow or exceed free-tier limits.

## Notes

- The app builds the Chroma index during image creation with `python index.py`.
- `cv.txt` must be present in the deployed source/image.
- Large model downloads and `torch` can make the image heavy; if needed, pre-bake model files or move model hosting elsewhere.
