# 📊 TCS Forecast Agent  
_An AI-powered financial forecasting system using Google Gemini, LangChain, and FastAPI._

---

## 🚀 Project Overview
**TCS Forecast Agent** automatically analyzes TCS quarterly and annual reports to predict next-quarter performance.  
It combines **data extraction**, **semantic retrieval**, and **LLM-based reasoning** to produce structured financial forecasts.

**Key design highlights:**
- Modular FastAPI backend for clean separation of logic.  
- Deterministic numeric extraction from PDFs using regex.  
- FAISS-based semantic search for contextual retrieval.  
- LangChain + Gemini for qualitative and forecast synthesis.  
- MySQL logging for complete request/response traceability.

---

## 🧠 Architecture
**Flow:**  
Extraction → Embedding (FAISS) → Retrieval → Gemini (via LangChain) → Forecast JSON → DB Log  

**Core modules:**
- `extractor.py` — Extracts metrics from reports  
- `embeddings_store.py` — Builds FAISS store  
- `tools.py` — Runs Gemini-based qualitative + market analysis  
- `main.py` — Orchestrates chain, synthesizes forecast  
- `db.py` — Logs requests/responses in MySQL  

---

## ⚙️ Setup Instructions
### 1️⃣ Clone & Setup Environment
```bash
git clone https://github.com/Soumya2000/TCS-forecast-agent.git
cd TCS-forecast-agent
python -m venv venv
venv\Scripts\activate       # or source venv/bin/activate
pip install -r requirements.txt
