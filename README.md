# Advanced-RAG-Series
This repository contains advanced LLM-based chatbots for Retrieval Augmented Generation (RAG) and Q&A with different databases. (VectorDB, GraphDB, SQLite, CSV, XLSX, etc.). The repository provides guide on using both AzureOpenAI and OpenAI API for each project. Each project is accompanied with a YouTube video that explains all the details. The link to the videos are provided in each section.

## List of projects:
- [x] [LangGraph_1o1_Agentic_Customer_Support](#LangGraph_1o1_Agentic_Customer_Support)
- [x] [AgentGraph-Intelligent-Q&A-and-RAG-System](#AgentGraph-Intelligent-Q&A-and-RAG-System)
- [x] [Q&A-and-RAG-with-SQL-and-TabularData](#Q&A-and-RAG-with-SQL-and-TabularData)
- [x] [KnowledgeGraph-Q&A-and-RAG-with-TabularData](#KnowledgeGraph-Q&A-and-RAG-with-TabularData)

## General structure of the projects:

```
Project-folder
  ├── README.md           <- The top-level README for developers using this project.
  ├── HELPER.md           <- Contains extra information that might be useful to know for executing the project.
  ├── .env                <- dotenv file for local configuration.
  ├── .here               <- Marker for project root.
  ├── configs             <- Holds yml files for project configs
  ├── explore             <- Contains my exploration notebooks and the teaching material for YouTube videos. 
  ├── data                <- Contains the sample data for the project.
  ├── src                 <- Contains the source code(s) for executing the project.
  |   └── utils           <- Contains all the necessary project modules. 
  └── images              <- Contains all the images used in the user interface and the README file. 
```
NOTE: This is the general structure of the projects, however there might be small changes duo to the specific needs of each project.

## Key Notes:
**Key Note 1:** All the project uses OpenAI models.

**Key Note 2 :** When we interact with databases using LLM agents, good informative column names can help the agents to navigate easier through the database.

**Key Note 3:** When we interact with sensitive databases using LLM agents, remember to NOT use the database with WRITE privileges. Use only READ and limit the scope. Otherwise your user can manupulate the data (e.g ask your chain to delete data).

**Key Note 4:** Familiarity with database query languages such as Pandas for Python, SQL, and Cypher can enhance the user's ability to ask more better questions and have a richer interaction with the graph agent.

## Project description:
<!-- ====================================== -->
<!-- LangGraph_1o1_Agentic_Customer_Support -->
<!-- ====================================== -->
<a id="AgentGraph-Intelligent-Q&A-and-RAG-System"></a>
<h3><a style=" white-space:nowrap; " href="https://github.com/Farzad-R/Advanced-QA-and-RAG-Series/tree/main/LangGraph_1o1_Agentic_Customer_Support"><b>LangGraph_1o1_Agentic_Customer_Support:</b></a></h3>

LangGraph_1o1_Agentic_Customer_Support is a project designed to demonstrate how complex systems can be built using LangGraph. In this project, we create an agentic customer service chatbot for Swiss Airlines in four different versions, addressing common real-world challenges at each step. The system supports a wide range of tasks through 18 tools, including Retrieval-Augmented Generation (RAG), web search, and travel planning.


**Features:**
- System Design: Demonstrates stable, effective strategies for building complex systems with LangGraph.
- Database Interaction: Provides methods for managing sensitive tasks such as writing, cleaning, and updating data in SQL databases.
- Workflow Integration: Combines multiple workflows into one seamless system, including web search, SQL database operations, and RAG on vector databases.
- Design strategies: Explores various strategies to address challenges and optimize system performance.

**YouTube video:**: [Link](TBD)

<!-- ========================================= -->
<!-- AgentGraph-Intelligent-Q&A-and-RAG-System -->
<!-- ========================================= -->
<a id="AgentGraph-Intelligent-Q&A-and-RAG-System"></a>
<h3><a style=" white-space:nowrap; " href="https://github.com/Farzad-R/Advanced-QA-and-RAG-Series/tree/main/AgentGraph-Intelligent-Q%26A-and-RAG-System"><b>AgentGraph-Intelligent-Q&A-and-RAG-System:</b></a></h3>

This project demonstrates how to build an agentic system using Large Language Models (LLMs) that can interact with multiple databases and utilize various tools. It highlights the use of SQL agents to efficiently query large databases. The key frameworks used in this project include OpenAI, LangChain, LangGraph, LangSmith, and Gradio. The end product is an end-to-end chatbot, designed to perform these tasks, with LangSmith used to monitor the performance of the agents.

**Features:**
- Handles unstructured data with RAG and structured data with SQL agents.
- Built-in web search when needed.
- Automatically chooses the best tool for each task.
- Scalable for large databases.
- Easily connects to multiple databases.

**YouTube video:**: [Link](https://youtu.be/xsCedrNP9w8?si=LdX45fMZuGhMCEoq)



<!-- ==================================== -->
<!-- Q&A-and-RAG-with-SQL-and-TabularData -->
<!-- ==================================== -->
<a id="Q&A-and-RAG-with-SQL-and-TabularData"></a>
<h3><a style=" white-space:nowrap; " href="https://github.com/Farzad-R/Advanced-RAG-Series/tree/main/Q&A-and-RAG-with-SQL-and-TabularData"><b>Q&A-and-RAG-with-SQL-and-TabularData:</b></a></h3>

`Q&A-and-RAG-with-SQL-and-TabularData` is a chatbot project that utilizes <u>GPT 3.5</u>, <u>Langchain</u>, <u>SQLite</u>, and <u>ChromaDB</u> and allows users to interact (perform <u>Q&A</u> and <u>RAG</u>) with SQL databases, CSV, and XLSX files using natural language.

**Features:**
- Chat with SQL data.
- Chat with preprocessed CSV and XLSX data.
- Chat with uploaded CSV and XSLX files during the interaction with the user interface.
- RAG with Tabular datasets.

**Databases:**
- Diabetes dataset: [Link](https://www.kaggle.com/datasets/akshaydattatraykhare/diabetes-dataset?resource=download&select=diabetes.csv)
- Cancer dataset: [Link](https://www.kaggle.com/datasets/rohansahana/breast-cancer-dataset-for-beginners?select=train.csv)
- Chinook SQL database: [Link](https://database.guide/2-sample-databases-sqlite/)

**YouTube video:** [Link](https://youtu.be/ZtltjSjFPDg?si=YdIeYcFeP4yzTXKQ)

<!-- =========================================== -->
<!-- KnowledgeGraph-Q&A-and-RAG-with-TabularData -->
<!-- =========================================== -->
<a id="KnowledgeGraph-Q&A-and-RAG-with-TabularData"></a>
<h3><a style=" white-space:nowrap; " href="https://github.com/Farzad-R/Advanced-RAG-Series/tree/main/KnowledgeGraph-Q&A-and-RAG-with-TabularData"><b>KnowledgeGraph-Q&A-and-RAG-with-TabularData:</b></a></h3>

`KnowledgeGraph-Q&A-and-RAG-with-TabularData` is a chatbot project that utilizes <u>knowledge graph</u>, <u>GPT 3.5</u>, <u>Langchain graph agent</u>, and <u>Neo4j</u> graph database and allows users to interact (perform <u>Q&A and RAG</u>) with Tabular databases (CSV, XLSX, etc.) using natural language. This project also demonstrates an approach for constructing the knowledge graph from unstructured data by leveraging LLMs.

**Features:**
- Chat with a graphDB created from tabular data.
- RAG with a graphDB created from tabular data.

**Databases:**
- Movie dataset: [Link](https://raw.githubusercontent.com/tomasonjo/blog-datasets/main/movies/movies_small.csv)
- Medical reports dataset: [Link](https://github.com/neo4j-partners/neo4j-generative-ai-azure/tree/main/ingestion/data)

**YouTube video:**: [Link](https://youtu.be/3NP1llvtrbI?si=pcL3_StQvqjjnkm9)
