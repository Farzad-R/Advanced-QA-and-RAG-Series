# ChatPub
This repository contains advanced LLM-based chatbots for RAG and Q&A with different databases. (VectorDB, GraphDB, SQLite, CSV, XLSX, etc.).

### List of projects:
- [x] [Chat-SQL-GPT](#Chat-SQL-GPT)
- [ ] [csvGraphChatGPT](#csvGraphChatGPT)
- [ ] [csvGraph-RAG-GPT](#csvGraph-RAG-GPT)
- [ ] [DocGraph-RAG-GPT](#DocGraph-RAG-GPT)

General structure of the projects:

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
  |   └── utils           <- Contains all the necesssary project's modules. 
  └── images              <- Contains all the images used in the user interface and the README file. 
```
NOTE: This is the general structure of the projects, however there might be small changes duo to the specific needs of each project.

## Project description:
<!-- ============= -->
<!-- Chat-SQL -->
<!-- ============= -->
<a id="Chat-SQL"></a>
<h3><a style=" white-space:nowrap; " href=""><b>Chat-SQL-GPT:</b></a></h3>
<p>
Chat-SQL-GPT is a chatbot that utilizes <u>GPT 3.5</u>, <u>Langchain</u>, and <u>SQLite</u> and allows users to interact (perform Q&A) with SQL databases using natrual language. It also allows them to chat with <u>CSV</u> and <u>XLSX</u> files by converting them automatically to SQLite database.

**Features:**

- Chat with SQL data.
- Chat with preprocessed CSV and XLSX data.
- Chat with uploaded CSV and XSLX files during the interaction with the user interface. 

**YouTube video:**: TBD