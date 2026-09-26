# AI ITSM Helpdesk Automation Platform

Hackathon MVP aligned to the Sorim.AI assessment.

## Stack
React + Vite | FastAPI | MongoDB Atlas | Hugging Face/open-source LLM | sentence-transformers | FAISS | ServiceNow/mock ServiceNow.

## Five required demos
1. My VPN is not connecting.
2. My password has expired.
3. How do I troubleshoot Outlook synchronization?
4. I need Visual Studio Code installed on my laptop.
5. Unsupported question -> no hallucination -> escalation.

## Run backend
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000

## Run frontend
cd frontend
npm install
npm run dev

Open http://localhost:5173

The backend works in mock/in-memory mode without credentials. Add MongoDB Atlas and ServiceNow credentials to backend/.env when available.

Swagger: http://localhost:8000/docs
