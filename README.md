# Advanced-RAG-Series
This repository contains advanced LLM-based chatbots for Retrieval Augmented Generation (RAG) and Q&A with different databases. (VectorDB, GraphDB, SQLite, CSV, XLSX, etc.). The repository provides guide on using both AzureOpenAI and OpenAI API for each project.

## List of projects:
- [x] [Q&A-and-RAG-with-SQL-and-TabularData](#Q&A-and-RAG-with-SQL-and-TabularData)
- [x] [KnowledgeGraph-Q&A-and-RAG-with-TabularData](#KnowledgeGraph-Q&A-and-RAG-with-TabularData)
- [ ] [KnowledgeGraph-Q&A-and-RAG-with-Text](#KnowledgeGraph-Q&A-and-RAG-with-Text) - **UNDER DEVELOPMENT**

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
**Key Note 1:** All the project uses Azure OpenAI. So, to use OpenAI API directly, just change the credentials and switch the models completions.

**Key Note 2 :** When we interact with databases using LLM agents, good informative column names can help the agents to navigate easier through the database.

**Key Note 3:** When we interact with databases using LLM agents, remember to NOT use the database with WRITE privileges. Use only READ and limit the scope. Otherwise your user can manupulate the data (e.g ask your chain to delete data).

**Key Note 4:** Familiarity with database query languages such as Pandas for Python, SQL, and Cypher can enhance the user's ability to ask more better questions and have a richer interaction with the graph agent.

## Project description:
<!-- ==================================== -->
<!-- Q&A-and-RAG-with-SQL-and-TabularData -->
<!-- ==================================== -->
<a id="Chat-SQL"></a>
<h3><a style=" white-space:nowrap; " href="https://github.com/Farzad-R/Advanced-RAG-Series/tree/main/Q&A-and-RAG-with-SQL-and-TabularData"><b>Q&A-and-RAG-with-SQL-and-TabularData:</b></a></h3>

`Q&A-and-RAG-with-SQL-and-TabularData` is a chatbot project that utilizes <u>GPT 3.5</u>, <u>Langchain</u>, <u>SQLite</u>, and <u>ChromaDB</u> and allows users to interact (perform <u>Q&A</u> and <u>RAG</u>) with SQL databases, CSV, and XLSX files using natrual language.

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

`KnowledgeGraph-Q&A-and-RAG-with-TabularData` is a chatbot project that utilizes <u>knowledge graph</u>, <u>GPT 3.5</u>, <u>Langchain graph agent</u>, and <u>Neo4j</u> graph database and allows users to interact (perform <u>Q&A and RAG</u>) with Tabular databases (CSV, XLSX, etc.) using natrual language. This project also demonstrates an approach for cunstructing the knowledge graph from unstructured data by leveraging LLMs.

**Features:**
- Chat with a graphDB created from tabular data.
- RAG with a graphDB created from tabular data.

**Databases:**
- Movie dataset: [Link](https://raw.githubusercontent.com/tomasonjo/blog-datasets/main/movies/movies_small.csv)
- Medical reports dataset: [Link](https://github.com/neo4j-partners/neo4j-generative-ai-azure/tree/main/ingestion/data)

**YouTube video:**: TBD


<!-- =============================== -->
<!-- Document-KnowledgeGraph-RAG-GPT -->
<!-- =============================== -->
