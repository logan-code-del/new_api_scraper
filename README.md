# News Cross-Reference API (Free, No API Keys)

[![Render Deploy Status](https://render.com/status/srv-d4aebha4d50c739vb3ng.svg)](https://render.com/deploy?repo=https://github.com/logan-code-del/new_api_scraper/)

**Note:** To get the status badge working, you need to replace `YOUR_SERVICE_ID` in the URL above with your actual Render service ID. You can find this ID in the URL of your service's dashboard on Render (it starts with `srv-`).

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
