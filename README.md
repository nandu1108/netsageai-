# NetSage AI

AI-powered troubleshooting assistant for Cisco-style lab networking issues.

This project builds a human-reviewed diagnosis workflow for Packet Tracer problems. Users provide symptoms and evidence such as VLAN configuration, IP settings, routes, ACLs, and show-command output. The app then suggests a likely root cause, affected OSI layer, next command to run, and fix steps. Every diagnosis is reviewed by a human before it is accepted.

## What is included

- 32 real-style troubleshooting cases across VLAN, DHCP, routing, ACL, NAT, DNS, and wireless issues
- Structured AI prompt templates for Cisco diagnosis output
- Deterministic rule checker for common misconfigurations
- FastAPI backend for troubleshooting and feedback logging
- Frontend dashboard for issue summary and human review tracking
- Responsible AI log with examples where the AI was corrected by a human

## Project structure

```bash
netsageai-/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── checker/
│   │   ├── models/
│   │   ├── parsers/
│   │   └── rag/
│   ├── data/
│   │   ├── cases.csv
│   │   ├── sample_rule_check_cases.json
│   │   ├── responsible_ai_log.md
│   │   └── faiss_index/
│   └── requirements.txt
├── frontend/
│   └── src/
├── diagnose_prompt.md
├── review_prompt.md
├── README.md
└── .gitignore
```

## Features implemented

### 1. Case dataset
A CSV dataset with 32 troubleshooting cases is included in [backend/data/cases.csv](backend/data/cases.csv). Each case contains:

- symptom
- topology note
- show output evidence
- expected fault
- OSI layer
- concept tag
- severity

### 2. AI diagnosis prompt library
The structured prompt templates are defined in [diagnose_prompt.md](diagnose_prompt.md) and [review_prompt.md](review_prompt.md). These are designed to require evidence-backed JSON outputs with fields such as:

- root cause
- confidence
- next command
- fix steps
- evidence

### 3. Rule-based checker
The deterministic Python checker in [backend/app/checker/rule_checker.py](backend/app/checker/rule_checker.py) validates common issues such as:

- duplicate IPs
- wrong subnet masks
- gateway mismatch
- interface down
- missing VLANs
- missing routes

### 4. Human review workflow
The frontend includes a review flow where the diagnosis must be accepted, edited, or rejected by a human. The backend logs outcomes under the feedback endpoint and aggregates them on the dashboard.

### 5. Dashboard summary
The frontend dashboard displays totals and verdict breakdowns, plus issue-type and severity summaries from the project dataset and feedback log.

## Setup

### 1. Backend environment

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then edit the new `.env` file and set your real Gemini key:

```bash
GEMINI_API_KEY=your_real_key_here
```

Now build the vector index required by the retrieval layer:

```bash
python -m app.rag.ingest
```

Start the backend:

```bash
PYTHONPATH=. uvicorn app.main:app --reload
```

### 2. Frontend

```bash
cd ../frontend
npm install
npm run dev
```

The frontend is configured to use the local backend at `http://localhost:8000/api` by default.

> Do not commit a real `.env` file with your API key. Use `.env.example` as the template and keep your actual key local.

## API endpoints

- POST `/api/troubleshoot` - diagnose a network problem
- POST `/api/feedback` - log human verdict for a diagnosis
- GET `/api/dashboard` - view summary metrics and review breakdown

## Responsible AI

The project explicitly includes a human review requirement before any fix is accepted. The log in [backend/data/responsible_ai_log.md](backend/data/responsible_ai_log.md) documents several cases where AI output was edited or rejected by a human reviewer.

## Team / project note

This project follows the NetSage AI assignment goal: AI-assisted troubleshooting with a safety check that keeps a human in the loop for every recommendation.

## Tech stack

- Python + FastAPI
- React + Vite
- Gemini API / LLM reasoning
- FAISS + retrieval
- CSV-based case dataset
- Deterministic networking validation rules
