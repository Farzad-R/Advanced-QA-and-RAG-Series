# 🤖 Connect LangGraph Agents to Real Databases with Docker

This project demonstrates how to build a **real-world, agentic chatbot** using **LangGraph**, powered by **OpenAI models**, and connect it to **persistent databases** for both vector-based retrieval (RAG) and memory.

It is designed for **learners, developers, and professionals** who want to go beyond toy examples and understand how to integrate real infrastructure components into LLM-based applications.

---

## 🚀 What This Project Covers

### ✅ 1. Agentic Chatbot with LangGraph

* Built using **LangGraph**, a state-machine-based framework for AI agents
* Supports both **Retrieval-Augmented Generation (RAG)** and **pure chat**
* Integrates with **OpenAI GPT models** (e.g., `gpt-4o`, `gpt-4-turbo`, etc.)
* Manages memory and conversation flow through LangGraph's node-based system

---

### ✅ 2. Real Databases for Production-Style Design

* **ChromaDB**: Used as the **vector database** to store document embeddings
* **PostgreSQL**: Used as the **memory backend** for LangGraph checkpointing
* Optional: **LangSmith** support for tracing, debugging, and analytics

---

### ✅ 3. 3-Container Microservice Architecture (via Docker Compose)

Each component runs in an isolated service:

* **Chatbot Container**: LangGraph backend + Gradio frontend
* **ChromaDB Container**: Persistent vector store accessed via `HttpClient`
* **PostgreSQL Container**: Persistent memory store for LangGraph

This approach mirrors real-world deployment environments and improves modularity, scalability, and portability.

---

### ✅ 4. Automatic VectorDB Creation in Chroma Container

* The vector database is **not created locally**, but **inside the Chroma container**.
* Achieved by using:

  ```python
  chromadb.HttpClient(host="chroma", port=8000)
  ```
* This ensures the vector data is accessible only via the running container just like it would be in production.

---

### ✅ 5. Visualize Docker Container Communication (with Weave Scope)

We include steps to **visually inspect the live communication** between containers using [Weave Scope](https://www.weave.works/oss/scope/).

You get:

* Real-time topology graph
* Communication metrics (who's talking to whom)
* CPU/Memory usage per container
* Logs and deep-inspection per service

> 📍 Accessible via `http://localhost:4040` after following our documented steps.

---

### ✅ 6. Development Best Practices

* Secrets managed via `.env` file
* Organized project structure (`src/`, `configs/`, `utils/`, `data/`, etc.)
* Custom logging system for debug and error tracing
* Blueprint-based Flask structure for future expansion
* Clean `docker-compose.yml` and multi-stage Dockerfile setup

---

## 💡 Why This Project Matters

In real-world systems:

* Temporary memory like in-memory dictionaries doesn’t scale
* You must persist conversations and embedding indices
* Containerizing each component lets you scale and deploy to cloud or microservices platforms
* Understanding how these systems interact (LangGraph, vector DB, memory DB, OpenAI, frontend) is **critical for production-readiness**

This project gives you that understanding, with working code and explanation.

---

## 📦 Project Structure

```
project-root/
├── src/
│   ├── app.py                  # Gradio UI + chatbot logic
│   ├── prepare_vectordb.py     # Build and save vector database
│   └── utils/                  # LangGraph, RAG logic, logging, config
├── data/
│   ├── pdf/                    # Raw input PDFs
│   └── vectordb/               # Persisted Chroma DB
├── config/
│   └── config.yml              # Model + DB settings
├── images/                     # UI assets
├── .env                        # API keys + database URIs
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Chatbot Dockerfile
├── docker-compose.yml          # 3-container deployment
├── README.md
```

---

## 🧪 Running Locally (Minimal Dev Setup)

### Ensure your `.env` includes:

```
OPENAI_API_KEY=your_openai_key
LANGCHAIN_API_KEY=your_langchain_key
DATABASE_URI=postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable
```

🔔 NOTE: The `DATABASE_URI` value differs depending on whether you're running the project locally or using the Docker-based microservice setup.

### 🐍 Step 1: Install dependencies

```bash
pip install -r requirements.txt
```

### 🧠 Step 2: Prepare the vector DB

```bash
python src/prepare_vectordb.py
```

### 🚀 Step 3: Run the chatbot

```bash
python src/app.py
```

---

## 🐳 Running with Microservices (3-Container Setup)

### ✅ Ensure your `.env` includes:

```env
OPENAI_API_KEY=your_openai_key
LANGCHAIN_API_KEY=your_langchain_key
DATABASE_URI=postgresql://postgres:postgres@postgres:5432/postgres
```

> **📌 NOTE:** `DATABASE_URI` points to the PostgreSQL container (`postgres`) from within the chatbot container. This value is different when running locally.

---

### 🚀 Step 1: Launch All Services

```bash
docker-compose up --build
```

This will:

* Start a **PostgreSQL container** for graph memory
* Start a **ChromaDB container** for vector retrieval
* Start the **Chatbot container**, exposing the Gradio interface at [http://localhost:7860](http://localhost:7860)

---

### 🔧 Step 1: Prepare Vector DB (Once)

You'll now build the vector database directly inside the chatbot container, using the running Chroma server.

```bash
docker exec -it chatbot python src/prepare_vectordb_container.py
```

This connects to the Chroma container via internal Docker networking (`host="chroma", port=8000`) and saves the vector data into the shared volume.

✅ Do this only once — unless you want to rebuild/update the DB.

---

## 🧠 Architecture Overview

```
[User] → [Gradio UI] 
       → [LangGraph-powered Backend]
            ├─→ OpenAI API
            ├─→ PostgreSQL (graph memory)
            └─→ ChromaDB (RAG vectors)
       → [Optional: LangSmith Tracing]
```

Each service runs in its own container:

| Container  | Role                           |
| ---------- | ------------------------------ |
| `chatbot`  | Gradio UI + LangGraph backend  |
| `postgres` | Stores persistent graph memory |
| `chroma`   | Stores and serves vector data  |

This architecture mirrors a real-world, production-style setup where services are **modular**, **interoperable**, and **easy to monitor or scale**.

---

## 📊 Visualizing Microservice Traffic with Weave Scope

You can use [Weave Scope](https://github.com/weaveworks/scope?tab=readme-ov-file) to visualize the live communication between your Docker containers.

### ✅ Works Best on Windows + WSL2 (Tested Setup)

In case you are using Docker with WSL just like me, follow these steps **in your WSL terminal**, not PowerShell or CMD:

### 1. Start the Weave Scope UI Container

```bash
docker run -d --name weave-scope \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 4040:4040 \
  weaveworks/scope
```

> This starts the visual dashboard server on [http://localhost:4040](http://localhost:4040)

---

### 2. Launch the Scope Probe via Installer Script

```bash
curl -L https://git.io/scope -o scope
chmod +x scope
./scope launch
```

> 🔁 This script creates another container to act as the **probe**, enabling full visibility into Docker container communication.

---

### 📍 Access the Dashboard

Once both commands are running, visit:

👉 [http://localhost:4040](http://localhost:4040)

You should see a full interactive UI showing:

* Your three main containers (`chatbot`, `postgres`, `chroma`)
* Network traffic
* Container details, logs, metrics

---

### 🔄 Stop and Restart Later

To stop both containers:

```bash
docker stop weave-scope weavescope
docker rm weave-scope weavescope
```

To restart:

```bash
# Repeat both steps above
```

> ✅ This dual-container setup was the only one reliably working on WSL2 in our tests. This may differ in native Linux or Mac environments.

---

## 🔐 Authentication and Memory Separation

* Each user is authenticated
* Each chat session gets a unique `thread_id`
* This isolates memory per session and user

---

## 📋 Logging

* Logs stored in `/logs`
* Rotates daily with levels: INFO, DEBUG, ERROR

---

## 📚 Learning Goals

You’ll learn how to:

* Design a chatbot using LangGraph
* Persist chat memory using PostgreSQL
* Use a real vector DB for RAG with Chroma
* Use `.env`, logging, and containerization for deployment
* Build production-ready pipelines for agentic LLM apps

---

## 📎 Resources

* [LangGraph Documentation](https://docs.langgraph.dev/)
* [ChromaDB](https://docs.trychroma.com/)
* [OpenAI Chat Models](https://platform.openai.com/docs/guides/gpt)
* [LangSmith (Optional)](https://smith.langchain.com/)

---

## 🧠 Want to Go Further?

* Replace Chroma with a managed vector DB like Pinecone or Qdrant
* Deploy containers to Fly.io, Railway, or AWS
* Add user dashboards to review memory history
* Implement multi-agent chains and tools

---

## 🙌 Built by \[Farzad Roozitalab / AI RoundTable]

If you found this helpful, consider subscribing on YouTube!

---

Happy building! 💡