# News Cross-Reference API (Free, No API Keys)

This API:
- Scrapes public RSS news feeds
- Extracts factual candidate statements
- Cross-references the claims across independent outlets
- Returns corroborated facts + unsupported claims

No API keys are required.

## Run locally

pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app:app --reload

## Deploy Free

### ✅ Render.com (best free option)

1. Push to GitHub  
2. New Web Service → select repo  
3. Build Command:
./build.sh

4. Start Command:
uvicorn app:app --host 0.0.0.0 --port $PORT


### ✅ Fly.io

flyctl launch
flyctl deploy

### ✅ Deta Space

deta new --python
deta deploy

---

# API Endpoints

- `/` – Status
- `/news` – Returns fact-checked news JSON
