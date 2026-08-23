# 🎓 CampusAI — Your College Assistant MVP

**CampusAI** is an AI-powered college assistant designed to answer student queries about college events, deadlines, clubs, courses, and notices with **ZERO hallucination**.

It relies strictly on local, verified college knowledge base data (`data/opportunities.json`, `data/notices.json`, `data/clubs.json`) and refuses to fabricate dates, fees, contact numbers, eligibility criteria, faculty coordinators, or registration URLs.

---

## 🌟 Key Features

1. **Zero Hallucination Guarantee**:
   - Responds strictly with grounded facts from college data.
   - Outputs: *"I don't have enough information in the college data to answer that confidently."* whenever information is missing (e.g. SIGGRAPH deadline or faculty coordinator).
2. **Intent Classification & Typo Tolerance**:
   - Handles misspelled words ("microsoft ambassdor", "edgenova fee", "gamejam"), slang, natural language, and short queries.
3. **Deadline Radar**:
   - Evaluates opportunity deadlines relative to the competition date (**19 August 2026**).
   - Badges:
     - 🔴 **Ending today** (AI Game Jam)
     - 🟠 **Due soon** (Microsoft Student Ambassadors)
     - 🟢 **Upcoming** (EDGENOVA'26, TEDxSRMIST)
     - ⚪ **Deadline unavailable** (SIGGRAPH SRM KTR)
4. **Smart Recommendation Engine**:
   - Maps student interests (AI, Coding, Design, Games, Research, Leadership, High Prize) to relevant opportunities.
   - Distinguishes **Known Fact** from **Recommendation based on known facts**.
5. **Notice Summarization**:
   - Generates structured markdown summaries for complex event notices (e.g., EDGENOVA'26).
6. **Comparison Engine**:
   - Generates comparative tables (e.g. EDGENOVA vs AI Game Jam, highest prize, cheapest entry).
7. **Offline Administrative Ingestion Pipeline**:
   - Allows judges/administrators to paste new notice text or JSON records via the UI or API (`/api/ingest`) to update the knowledge base live without code changes or server restarts.

---

## 🛠️ Technology Stack

- **Backend**: Python 3 Standard Library (`http.server`, `json`, `re`, `datetime`, `unittest`)
  - **Zero Third-Party Dependencies**: No `pip install` required, runs 100% offline.
- **Frontend**: Modern Vanilla HTML5, CSS3 (Dark Glassmorphic UI), and ES6+ JavaScript.
- **Architecture**: Single-threaded / Multi-threaded HTTP Server serving both REST API endpoints and web app frontend.

---

## 🚀 How to Run

### Quick Start (One-Click)

From the project root directory:

```bash
./run.sh
```

Or run directly with Python 3:

```bash
python3 backend/api/server.py 8000
```

Open your web browser at:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🧪 Running Automated Unit Tests

Execute the 8 automated test cases verifying retrieval, deadline logic, recommendations, misspelling tolerance, and zero-hallucination refusals:

```bash
python3 -m unittest tests/test_campus_ai.py -v
```

---

## 📁 File & Directory Structure

```text
campus-ai/
│
├── data/
│   ├── opportunities.json       # Database of college hackathons, recruitments, competitions
│   ├── notices.json             # Official notices and raw text
│   └── clubs.json               # Technical & student chapter directory
│
├── backend/
│   ├── api/
│   │   └── server.py            # Multithreaded HTTP Server & REST API endpoints
│   ├── retrieval/
│   │   └── engine.py            # Field-aware local search & scoring engine
│   ├── reasoning/
│   │   ├── query_parser.py      # Intent classifier & typo normalization
│   │   ├── answer_generator.py  # Fact-grounded answer & notice summary generator
│   │   ├── recommender.py       # Domain & interest mapping engine
│   │   └── deadline.py          # Date evaluation & Deadline Radar
│   ├── validation/
│   │   └── guardrails.py        # Hallucination guardrail & refusal filter
│   └── ingestion/
│       └── ingest.py            # Notice/Poster text parser & knowledge base updater
│
├── frontend/
│   ├── index.html               # Main Web Application UI
│   ├── css/
│   │   └── styles.css           # Glassmorphic dark design system
│   └── js/
│       ├── api.js               # API service client
│       ├── components.js        # Markdown & UI component renderer
│       └── app.js               # Event handling & state management
│
├── tests/
│   └── test_campus_ai.py        # Automated test suite (8 test cases)
│
├── README.md                    # Setup & documentation
└── run.sh                       # One-click startup script
```

---

## 📥 How to Add New College Information Later

To add new notices or event posters to CampusAI without touching application code:

1. **Option A (Via Web UI)**:
   - Click the **"📥 Ingest Notice"** button in the top navigation bar.
   - Paste raw notice text or a structured JSON record matching `opportunities.json`.
   - Click **"Ingest into Knowledge Base"**.

2. **Option B (Via API)**:
   ```bash
   curl -X POST http://localhost:8000/api/ingest \
     -H "Content-Type: application/json" \
     -d '{"text": "Hackathon on Web3 by CINTEL on Sep 15, 2026. Prize ₹10,000."}'
   ```

3. **Option C (Direct Data File Edit)**:
   - Add new JSON objects to `data/opportunities.json`.
