# RAG Evolution — Advanced QA & RAG Series

A hands-on lab of modern **Retrieval-Augmented Generation (RAG)** techniques—built to compare strategies side-by-side on the same stack. Spin it up, pick a strategy, ask questions, and measure the difference.

> Strategies included: **Simple RAG w/ Memory, Corrective RAG (CRAG), Adaptive RAG, Self-RAG, Fusion RAG, Speculative RAG, Agentic RAG, HyDE**.

---

## 🧭 Table of Contents

* [Features](#features)
* [Architecture](#architecture)
* [Quickstart](#quickstart)
* [Data & Vector DB](#data--vector-db)
* [Usage](#usage)
* [Strategies](#strategies)
* [Project Structure](#project-structure)
* [Config & Environment](#config--environment)
* [Troubleshooting](#troubleshooting)
* [Contributing](#contributing)
* [License](#license)

---

## ✨ Features

* Pluggable **RAG strategies** behind a common interface.
* **Chroma** vector store (synthetic dataset generator included).
* One-command **local app**: choose a strategy, ask a question.
* Clear separation of **data processing** vs **inference**.
* Easy to extend with your own documents.

---

## 🏗️ Architecture

```
User Query
   │
   ▼
[Strategy Router / Menu]
   │
   ├── Simple RAG + Memory
   ├── Corrective RAG (grader + re-retrieval)
   ├── Adaptive RAG (complexity-based)
   ├── Self-RAG (reflect + verify)
   ├── Fusion RAG (multi-source/results fusion)
   ├── Speculative RAG (drafter + verifier)
   ├── Agentic RAG (planner/researcher/synthesizer)
   └── HyDE (hypothetical doc embeddings)
   │
   ▼
Retriever (Chroma) ⇄ Embeddings
   │
   ▼
Generator (LLM)
   │
   ▼
Answer (+ optional citations/notes)
```

---

## ⚡ Quickstart

```bash
# Clone
git clone https://github.com/Farzad-R/Advanced-QA-and-RAG-Series.git
cd rag-evolution

# Create new environment with Python 3.11
python3.11 -m venv venv

# Activate
source venv/bin/activate
# (Windows PowerShell) .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

## 📚 Data & Vector DB

You have two options:

### 1) Generate a synthetic vector DB (quick demo)

```bash
# From project root
python src/data_processor.py
```

### 2) Use your own documents

* Add your docs to the appropriate `data/` location (see project structure).
* Build a Chroma vector DB from your docs.
  *(If you need a walkthrough, see my other RAG projects for doc ingestion → Chroma build steps.)*

---

## ▶️ Usage

Run the app and choose a strategy from the menu:

```bash
# From project root
python src/app.py
```

* Select the desired **RAG strategy**.
* Ask your question.
* Review the model’s response (and optional notes/citations depending on strategy).

---

## 🧪 Strategies

| Technique                 | What it adds                                    | Typical win                       |
| ------------------------- | ----------------------------------------------- | --------------------------------- |
| **Simple RAG w/ Memory**  | Session/user context recall                     | Personalization & coherence       |
| **Corrective RAG (CRAG)** | Grade retrieved docs, re-retrieve if weak       | Reliability on incomplete corpora |
| **Adaptive RAG**          | Vary retrieval depth by query complexity        | Efficiency & responsiveness       |
| **Self-RAG**              | Reflect, decide to retrieve, verify claims      | Factual robustness                |
| **Fusion RAG**            | Multi-retrieval + result fusion                 | Coverage of siloed sources        |
| **Speculative RAG**       | Small model drafts, large model verifies        | Speed at scale, cost control      |
| **Agentic RAG**           | Planner/Researcher/Synthesizer (+ tools)        | Multi-step reasoning & tools      |
| **HyDE**                  | Generate hypothetical answer → embed → retrieve | Zero-shot recall, quirky phrasing |

---

## 📁 Project Structure

```
rag-evolution/
├─ src/
│  ├─ app.py                # Entry point: select strategy & Q&A loop
│  ├─ data_processor.py     # Build synthetic dataset & Chroma index
│  └─ rag_techniques/       # Strategy implementations / router
├─ data/
│  └─ chroma_db/             # Chroma persistent store
├─ requirements.txt
├─ README.md
├─ .here                    # Required for using pyprojroot
├─ queries.txt              # Sample queries
├─ references.txt           # References that were used to implement this project
└─ .env.example             # (Optional) environment template
```

---

## 🔧 Config & Environment

If your strategies require model/provider keys, export them before running:

```bash
# Example (adjust to your provider)
export OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# or
export ANTHROPIC_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxx
# or
export COHERE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

You can also place them in a local `.env` and load via your preferred method.

---

## 🛠️ Troubleshooting

* **Module not found / imports:** Ensure you’re running from project root and the venv is active.
* **No results from retriever:** Build the vector DB first (`python src/data_processor.py`) or ingest your docs.
* **API errors:** Verify your API key is exported and your account has access to the selected model.

---

## 🤝 Contributing

PRs welcome! Ideas that help:

* Add a new strategy or a variant/ablation.
* Plug in evaluation (latency, accuracy, token cost).
* Add ingestion pipelines for new formats (PDF, HTML, Slack, Jira, etc.).

Open an issue to discuss major changes before submitting a PR.

---

**Have fun experimenting!**
Pick a strategy, ask a question, and see how retrieval choices shape answers.
