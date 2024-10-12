
---

# AgentGraph: Intelligent SQL-agent Q&A and RAG System for Chatting with Multiple Databases

This project demonstrates how to build an agentic system using Large Language Models (LLMs) that can interact with multiple databases and utilize various tools. It highlights the use of SQL agents to efficiently query large databases. The key frameworks used in this project include OpenAI, LangChain, LangGraph, LangSmith, and Gradio. The end product is an end-to-end chatbot, designed to perform these tasks, with LangSmith used to monitor the performance of the agents.

---

## Video Explanation: 
A detailed explanation of the project is available in the following YouTube video:

Automating LLM Agents to Chat with Multiple/Large Databases (Combining RAG and SQL Agents): [Link](https://youtu.be/xsCedrNP9w8?si=v-3k-BoDky_1IRsg)

---

## Requirements

- **Operating System:** Linux or Windows (Tested on Windows 11 with Python 3.9.11)
- **OpenAI API Key:** Required for GPT functionality.
- **Tavily Credentials:** Required for search tools (Free from your Tavily profile).
- **LangChain Credentials:** Required for LangSmith (Free from your LangChain profile).
- **Dependencies:** The necessary libraries are provided in `requirements.txt` file.
---

## Installation and Execution

To set up the project, follow these steps:

1. Clone the repository:
   ```bash
   git clone <repo_address>
   ```
2. Install Python and create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Download the travel sql database from this link and paste it into the `data` folder.

6. Download the chinook SQL database from this link and paste it into the `data` folder.

7. Prepare the `.env` file and add your `OPEN_AI_API_KEY`, `TAVILY_API_KEY`, and `LANGCHAIN_API_KEY`.

8. Run `prepare_vector_db.py` module once to prepare both vector databases.
   ```bash
   python src\prepare_vector_db.py
   ```
9. Run the app:
   ```bash
   python src\app.py
   ```
Open the Gradio URL generated in the terminal and start chatting.

*Sample questions are available in `sample_questions.txt`.*

---

### Using Your Own Database

To use your own data:
1. Place your data in the `data` folder.
2. Update the configurations in `tools_config.yml`.
3. Load the configurations in `src\agent_graph\load_tools_config.py`.

For unstructured data using Retrieval-Augmented Generation (RAG):
1. Run the following command with your data directory's configuration:
   ```bash
   python src\prepare_vector_db.py
   ```

All configurations are managed through YAML files in the `configs` folder, loaded by `src\chatbot\load_config.py` and `src\agent_graph\load_tools_config.py`. These modules are used for a clean distribution of configurations throughout the project.

Once your databases are ready, you can either connect the current agents to the databases or create new agents. More details can be found in the accompanying YouTube video.

---

## Project Schemas

### High-level overview

<div align="center">
  <img src="images/high-level.png" alt="high-level">
</div>

### Detailed Schema

<div align="center">
  <img src="images/detailed_schema.png" alt="detailed_schema">
</div>

### Graph Schema

<div align="center">
  <img src="images/graph_image.png" alt="graph_image">
</div>

### SQL-agent for large databases strategies

<div align="center">
  <img src="images/large_db_strategy.png" alt="large_db_strategy">
</div>

---

## Chatbot User Interface

<div align="center">
  <img src="images/UI.png" alt="ChatBot UI">
</div>

---

## LangSmith Monitoring System

<div align="center">
  <img src="images/langsmith.png" alt="langsmith">
</div>

---

## Databases Used

- **Travel SQL Database:** [Kaggle Link](https://www.kaggle.com/code/mpwolke/airlines-sqlite)
- **Chinook SQL Database:** [Sample Database](https://database.guide/2-sample-databases-sqlite/)
- **stories VectorDB**
- **Airline Policy FAQ VectorDB**
---

## Key Frameworks and Libraries

- **LangChain:** [Introduction](https://python.langchain.com/docs/get_started/introduction)
- **LangGraph**
- **LangSmith**
- **Gradio:** [Documentation](https://www.gradio.app/docs/interface)
- **OpenAI:** [Developer Quickstart](https://platform.openai.com/docs/quickstart?context=python)
- **Tavily Search**
---