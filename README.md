# JobShield AI 🛡️
### Smart Internship & Job Risk Assessment Engine
> **AI-Powered Recruitment Safety Platform**  
> *"Flags warning signs and explains what to verify — never claims a final fraud verdict."*

---

## 🏆 Hackathon Project Pitch Overview

* **Project Name:** JobShield AI
* **Team:** **HackNova**
* **Team Members:**
  * **Harsh Pandey**
  * **Shivam Yadav**
  * **Mahi Garg**
  * **Priyanshi Bansal**

---

## 📌 Problem Statement & Target Audience

### The Problem
College students and fresh graduates receive internship and entry-level job offers through email, messaging apps (Telegram/WhatsApp), and online job portals. A growing number of these offers contain deceptive warning signs:
* Demands for upfront "registration", "training", or "laptop security" fees.
* Unclear or spoofed recruiter identities (e.g., using personal `@gmail.com` accounts pretending to be multinational corporations).
* Unrealistic promises (e.g., direct selection without interviews, astronomical compensation for low-skill tasks).
* Incomplete or missing company credentials (no registered address, missing CIN/GST numbers).

### Who Needs It?
* 🎓 **College Students:** Looking for safe, verified internships.
* 👨‍🎓 **Fresh Graduates:** Applying for their first jobs.
* 🏫 **Placement & Career Guidance Cells:** Reviewing unsolicited offers shared with students.
* 🤝 **Student Clubs & Career Mentors:** Supporting applicants and raising campus awareness.

**The Need:** A quick, understandable first-check that helps students pause, investigate, and make informed decisions.

---

## 🚀 The 4-Step Assessment Workflow

```
[01 SUBMIT] ────────► [02 EXTRACT] ────────► [03 ANALYZE] ────────► [04 EXPLAIN]
Paste job text        Read role, company,    Rules + NLP identify   Risk level, reasons,
or upload PDF         pay, fees & contacts   suspicious indicators  & next-step checklist
```

1. **01 SUBMIT:** Paste job posting text / chat transcript or upload an offer letter PDF (`.pdf` or `.txt`).
2. **02 EXTRACT:** High-performance PyMuPDF (`fitz`) and NLP regex parser automatically extract company name, role designation, stipend/salary, upfront fee demands, recruiter email domains, phone numbers, and messaging channels.
3. **03 ANALYZE:** Evaluates the document across 5 weighted safety vectors:
   * **Financial Demands & Upfront Fees** (Critical)
   * **Communication & Contact Channels** (High)
   * **Promise Realism & Effort-Reward Disconnect** (Medium-High)
   * **Role Clarity & Task Specificity** (Medium)
   * **Pressure Tactics & Artificial Scarcity** (Medium)
4. **04 EXPLAIN:** Generates an explainable safety score (0–100), risk tier (LOW, MEDIUM, HIGH), contextual reasons linked to exact text excerpts, multi-dimensional Chart.js radar visualization, and an interactive verification checklist.

---

## ✨ Key Features & Innovation

* **Document Reading:** Seamlessly extracts text and metadata from PDF offer letters using PyMuPDF (`fitz`) with OCR/PyPDF fallback.
* **Explainable Risk Report:** Every detected red flag is tied to the exact excerpt found in the document, explaining *why* it deserves attention and *what specific action* the student should take.
* **Anti-Fraud Negation Intelligence:** Distinguishes genuine fee demands from corporate anti-scam warnings (e.g., "The company never solicits training fees").
* **Interactive Verification Checklist:** Practical steps students can tick off in real-time (MCA registry lookup, domain validation, LinkedIn recruiter check, zero-fee enforcement) with browser persistence.
* **Placement Cell History Archive:** Centralized dashboard tracking scanned offers, risk distribution percentages, and aggregate safety metrics.
* **One-Click Test Presets:** Pre-loaded test cases (🔴 Scam with ₹1,850 fee, 🟡 Ambiguous typing job, 🟢 Verified InnovateLabs software engineering offer).
* **PDF Dossier Export:** Clean print-to-PDF formatting for sharing reports with parents, placement officers, and mentors.

---

## 🛠️ Technology Stack & Architecture

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5 | Responsive, modern cybersecurity UI with dark/light mode accents |
| **Backend** | Python 3 + Flask | Application routing, validation, and session handling |
| **AI / NLP** | Rule Engine + Heuristic NLP Parser | 5-vector risk calculation, negation parsing, explainable reasoner |
| **Documents** | PyMuPDF (`fitz`) + PyPDF | High-performance structural PDF text & metadata extraction |
| **Database** | SQLite (`jobshield.db`) | Assessment history, aggregate campus analytics, student feedback |
| **Visualization** | Chart.js | Interactive 5-dimensional risk radar chart & score gauge |

### Privacy & Responsible Use Principles
* **MVP Privacy Principle:** Documents are processed in-memory for risk evaluation; uploaded files are deleted immediately after extraction without persistent personal storage.
* **Not a Fraud Verdict:** Risk scores are educational indicators, not legal conclusions or employer blacklists.
* **Verify Independently:** Users are guided to authenticate details through verified government and corporate registries.

---

## 📂 Project Directory Structure

```
JobShield-AI/
├── app.py                     # Flask application entry point and routes
├── config.py                  # App configuration & upload limits
├── database.py                # SQLite persistence (Scans, feedback, metrics)
├── analysis_engine.py         # Rules + NLP risk assessment engine
├── document_extractor.py      # PyMuPDF extraction & text sanitization
├── samples.py                 # Pre-loaded benchmark test offers
├── test_suite.py              # Automated unit and integration test suite
├── create_sample_pdfs.py      # Script to generate sample PDF offer letters
├── requirements.txt           # Project dependencies
├── test_samples/              # Sample PDF offer letters for testing
│   ├── sample_scam_offer.pdf
│   └── sample_legit_offer.pdf
├── static/
│   ├── css/
│   │   └── style.css          # Sleek hackathon dashboard styling
│   └── js/
│       ├── main.js            # Drag & drop, sample loader, checklist logic
│       └── charts.js          # Chart.js radar & gauge visualizers
└── templates/
    ├── base.html              # Base layout with navbar, HackNova banner & footer
    ├── index.html             # Main scanner page (Paste text / Upload PDF)
    ├── results.html           # Detailed report (Score, radar, flags, checklist)
    ├── history.html           # Placement cell scan archive & metrics
    ├── guide.html             # Student recruitment safety handbook
    └── about.html             # Hackathon pitch, team profile & architecture
```

---

## 🏃 Getting Started & Local Execution

### 1. Prerequisites
* Python 3.10+ installed on your computer.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests
Verify that all unit tests, extraction pipelines, and web endpoints pass:
```bash
python test_suite.py
```

### 4. Start the Application
```bash
python app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Testing the Application

1. **Test with 1-Click Samples:**
   * On the home page, click any of the 3 presets on the right column (e.g. *"🔴 High Risk: Training Fee & Telegram Recruiter Scam"*).
   * Click **"Run JobShield AI Assessment"** to inspect the instant risk report.

2. **Test with Real PDF Uploads:**
   * Switch to the **"Upload Offer Letter (PDF / TXT)"** tab.
   * Drag & drop `test_samples/sample_scam_offer.pdf` or `test_samples/sample_legit_offer.pdf`.
   * Click **"Extract & Analyze PDF"** to see PyMuPDF parse and score the document in real time.

---

## 🗺️ Product Roadmap

* **Phase 1: MVP (Completed)**
  * Text paste and PDF offer letter extraction
  * 5-vector heuristic rule & NLP assessment engine
  * Interactive Chart.js radar and gauge visualization
  * SQLite scan history and campus safety metrics
* **Phase 2: BETA (Active)**
  * Contextual LLM summary expansion
  * Student feedback and false-positive reporting loop
  * Checklist completion persistence across sessions
* **Phase 3: Campus Pilot (Next)**
  * Direct Ministry of Corporate Affairs (MCA) API integration
  * Placement cell supervisor dashboard for bulk batch verification
  * University-wide recruiter whitelist registry

---

## 👥 HackNova Team Credits
* **Harsh Pandey**
* **Shivam Yadav**
* **Mahi Garg**
* **Priyanshi Bansal**

*Built with passion to protect students, promote transparent hiring, and make campus recruitment safer.*
