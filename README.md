# NetSage AI

AI-Powered Intelligent Network Troubleshooting and Configuration Assurance Assistant
for Cisco Packet Tracer-based networks.

This is a **starter scaffold** based on the project documentation (`docs/cisco_ps.pdf`
concept). It implements the core architecture — deterministic config parsers, a
RAG pipeline over a Cisco knowledge base, an LLM reasoning layer, and a FastAPI
backend — so you have a working skeleton to build features on top of.

## Project Structure

```
netsage-ai/
├── backend/
│   ├── app/
│   │   ├── parsers/          # Deterministic Python analysis engine
│   │   │   ├── vlan_parser.py
│   │   │   ├── ip_dhcp_parser.py
│   │   │   ├── routing_parser.py
│   │   │   └── acl_parser.py
│   │   ├── rag/               # RAG pipeline (embeddings + FAISS + LLM)
│   │   │   ├── ingest.py
│   │   │   ├── retriever.py
│   │   │   └── reasoner.py
│   │   ├── api/
│   │   │   └── routes.py      # FastAPI endpoints
│   │   ├── models/
│   │   │   └── schemas.py     # Pydantic request/response models
│   │   └── main.py            # FastAPI app entrypoint
│   ├── data/
│   │   ├── knowledge_base/    # Cisco docs (txt) to embed for RAG
│   │   └── sample_configs/    # Example VLAN/IP/routing/ACL configs (fault-injected)
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/        # DiagnosisReport, DashboardStats, ProblemForm
│       └── pages/             # App.jsx entry
└── docs/
    └── cisco_ps.pdf           # Original project brief
```

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Add your LLM API key
export GEMINI_API_KEY="your-key-here"   # or OPENAI_API_KEY

# Build the FAISS index from the knowledge base
python -m app.rag.ingest

# Run the API
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs` once running.

### Frontend

The `frontend/` folder has component stubs only (this scaffold focuses on the
AI/backend pipeline, which is the harder engineering problem). Wire these into
a Vite/CRA React app with Tailwind, pointing API calls at
`http://localhost:8000`.

## How the Pipeline Works

1. **User submits a problem** (e.g. "Faculty cannot access server") plus
   supporting data (VLAN configs, IP settings, routing table, ACL rules).
2. **Deterministic parsers** (`app/parsers/`) run first — they diff expected
   vs actual VLANs, check subnet/gateway consistency, look for missing routes,
   and scan ACL rules for blocking DENY statements. This layer needs no AI and
   catches the majority of common misconfigurations reliably.
3. **RAG retrieval** (`app/rag/retriever.py`) takes the parser findings +
   user complaint, embeds the query, and pulls the most relevant chunks from
   the Cisco knowledge base via FAISS.
4. **LLM reasoning** (`app/rag/reasoner.py`) combines retrieved context +
   parser findings into a prompt, and the LLM returns a structured diagnosis:
   root cause, affected layer, confidence, fix, and verification steps.
5. **Feedback** on each diagnosis (Correct / Partially Correct / Wrong) is
   logged to build an evaluation dataset over time.

## Next Steps to Extend This Scaffold

- [ ] Populate `data/knowledge_base/` with real Cisco documentation (VLAN,
      routing, DHCP, ACL command references)
- [ ] Add more fault-injection sample configs under `data/sample_configs/`
- [ ] Build out the React frontend (problem input form, diagnosis report view,
      dashboard with device/issue stats)
- [ ] Add a persistence layer (SQLite/Postgres) for feedback logging —
      currently stubbed to a local JSON file
- [ ] Wire in real Cisco Packet Tracer exports instead of the sample text configs
- [ ] Add authentication if this will be multi-user

## Tech Stack (per project brief)

| Component | Technology |
|---|---|
| Frontend | React / HTML-CSS-JS, Tailwind CSS |
| Backend | Python FastAPI |
| AI | Gemini API / OpenAI API, LangChain, Sentence Transformers |
| Vector Database | FAISS |
| Data Processing | Python, Pandas, JSON/YAML parsing |
| Network Simulation | Cisco Packet Tracer |
