# Projects API

FastAPI backend for the Project Generator. Uses Google Gemini to generate portfolio project ideas and MongoDB (via Motor) for persistence.

## Setup with Docker

1. Copy the env template and fill in your values:

   ```bash
   cp .env.example .env
   ```

   Required variables: `MONGO_URI`, `DB_NAME`, `GEMINI_API_KEY`, `API_KEY`, `ALLOWED_ORIGINS`.

2. Build the image:

   ```bash
   docker build -t projects-api .
   ```

3. Run the container:

   ```bash
   docker run --rm -p 8000:8000 --env-file .env projects-api
   ```

The API is then available at `http://localhost:8000` — docs at `/docs`, health check at `/health`.
