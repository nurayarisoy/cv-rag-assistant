Deployment options

1) Build & publish container (recommended)

 - The repository already contains a `Dockerfile` and a GitHub Actions workflow that pushes to GitHub Container Registry (`ghcr.io`).
 - Push your code to `main` to trigger the workflow. The image will be published to `ghcr.io/<owner>/<repo>:latest`.

2) Run on a VPS (DigitalOcean, AWS EC2)

 - Pull the image from GHCR and run it with:

 ```bash
 docker run -d -p 5001:5001 ghcr.io/<owner>/<repo>:latest
 ```

 - If you prefer to build on the server, clone the repo and run:

 ```bash
 docker build -t cv-rag-assistant:latest .
 docker run -d -p 5001:5001 cv-rag-assistant:latest
 ```

3) Render / Railway

 - Use private Docker image from GHCR or connect repo and use the Dockerfile directly.
 - Note: heavy model downloads may exceed free plan limits.

Notes:
- Large model downloads and `torch` may make the image big; consider pre-baking models into the image or hosting the model separately (Hugging Face).
- For automated deploy to a specific provider I will need access/credentials or you can run the above commands locally/remote.
