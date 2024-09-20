
---

# AgentGraph: Intelligent SQL-agent Q&A and RAG System for Chatting with Different Databases

This project demonstrates how to build an agentic system using Large Language Models (LLMs) that can interact with multiple databases and utilize various tools. It highlights the use of SQL agents to efficiently query large databases. The key frameworks used in this project include OpenAI, LangChain, LangGraph, LangSmith, and Gradio. The end product is an end-to-end chatbot, designed to perform these tasks, with LangSmith used to monitor the performance of the agents.

**Video Explanation:**  
A detailed explanation of the project is available in the following YouTube video:  
*Link: To be added*

---

## Requirements

- **Operating System:** Linux or Windows (Tested on Windows 11 with Python 3.9.11)
- **OpenAI API Key:** Required for GPT functionality.
- **Tavily Credentials:** Required for search tools (Free from your Tavily profile).
- **LangChain Credentials:** Required for LangSmith (Free from your LangChain profile).

---

## Installation

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

---

## Execution

### Running the Chatbot
All necessary data is included in the GitHub repository. To run the chatbot:

```bash
python src\app.py
```

1. Open the Gradio URL generated in the terminal.
2. Start chatting!

*Sample questions are available in `sample_questions.txt`.*

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

## Features to Be Improved
- Memory enhancements
- User and database authentication
- Error handling
- Database management and data pipeline improvements

---

## Project Structure

<div align="center">
  <img src="images/project_schema.png" alt="Schema">
</div>

---

## Chatbot User Interface

<div align="center">
  <img src="images/UI.png" alt="ChatBot UI">
</div>

---

## Databases Used

- **Diabetes Dataset:** [Kaggle Link](https://www.kaggle.com/datasets/akshaydattatraykhare/diabetes-dataset?resource=download&select=diabetes.csv)
- **Cancer Dataset:** [Kaggle Link](https://www.kaggle.com/datasets/rohansahana/breast-cancer-dataset-for-beginners?select=train.csv)
- **Chinook Database:** [Sample Database](https://database.guide/2-sample-databases-sqlite/)

---

## Key Frameworks and Libraries

- **LangChain:** [Introduction](https://python.langchain.com/docs/get_started/introduction)
- **Gradio:** [Documentation](https://www.gradio.app/docs/interface)
- **OpenAI:** [Developer Quickstart](https://platform.openai.com/docs/quickstart?context=python)
- **SQLAlchemy:** [Documentation](https://www.sqlalchemy.org/)

---

### Note:
This project is currently not production-ready. Key areas for improvement include enhancing memory, adding authentication layers, and implementing better error handling.

---

This README keeps it simple, professional, and easy to follow, offering clear instructions while maintaining the technical depth of the project. Let me know if you'd like any further adjustments!