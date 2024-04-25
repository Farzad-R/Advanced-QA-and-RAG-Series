# Advanced-RAG-Series
This repository contains advanced LLM-based chatbots for Retrieval Augmented Generation (RAG) and Q&A with different databases. (VectorDB, GraphDB, SQLite, CSV, XLSX, etc.). The repository provides guide on using both AzureOpenAI and OpenAI API for each project.

## List of projects:
- [x] [SQL-TabularData-Q&A-RAG-GPT](#SQL-TabularData-Q&A-RAG-GPT)
- [x] [TabularData-KnowledgeGraph-RAG-GPT](#TabularData-KnowledgeGraph-RAG-GPT)
- [ ] [Doc-KnowledgeGraph-RAG-GPT](#Doc-KnowledgeGraph-RAG-GPT)

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

## Project description:
<!-- =========================== -->
<!-- SQL-TabularData-Q&A-RAG-GPT -->
<!-- =========================== -->
<a id="Chat-SQL"></a>
<h3><a style=" white-space:nowrap; " href=""><b>SQL-TabularData-Q&A-RAG-GPT:</b></a></h3>
<p>
`SQL-TabularData-Q&A-RAG-GPT` is a chatbot that utilizes <u>GPT 3.5</u>, <u>Langchain</u>, <u>SQLite</u>, and <u>ChromaDB</u> and allows users to interact (perform <u>Q&A</u> and <u>RAG</u>) with SQL databases, CSV, and XLSX files using natrual language.

**Features:**
- Chat with SQL data.
- Chat with preprocessed CSV and XLSX data.
- Chat with uploaded CSV and XSLX files during the interaction with the user interface.
- RAG with Tabular datasets.

**Databases:**
- Diabetes dataset: [Link](https://www.kaggle.com/datasets/akshaydattatraykhare/diabetes-dataset?resource=download&select=diabetes.csv)
- Cancer dataset: [Link](https://www.kaggle.com/datasets/rohansahana/breast-cancer-dataset-for-beginners?select=train.csv)
- Chinook SQL database: [Link](https://database.guide/2-sample-databases-sqlite/)

**YouTube video:**: TBD

<!-- ================================== -->
<!-- TabularData-KnowledgeGraph-RAG-GPT -->
<!-- ================================== -->
<a id="TabularData-KnowledgeGraph-RAG-GPT"></a>
<h3><a style=" white-space:nowrap; " href=""><b>Chat-SQL-GPT:</b></a></h3>
<p>
`TabularData-KnowledgeGraph-RAG-GPT` is a chatbot that utilizes <u>knowledge graph</u>, <u>GPT 3.5</u>, <u>Langchain graph agent</u>, and <u>Neo4j</u> graph database and allows users to interact (perform <u>Q&A and RAG</u>) with Tabular databases (CSV, XLSX, etc.) using natrual language. This project also demonstrates an approach for cunstructing the knowledge graph from unstructured data by leveraging LLMs.

**Features:**
- Chat with a graphDB created from tabular data.
- RAG with a graphDB created from tabular data.

**Databases:**
- Movie dataset: [Link](https://raw.githubusercontent.com/tomasonjo/blog-datasets/main/movies/movies_small.csv)
- Medical reports dataset: [Link](https://github.com/neo4j-partners/neo4j-generative-ai-azure/tree/main/ingestion/data)

**YouTube video:**: TBD
