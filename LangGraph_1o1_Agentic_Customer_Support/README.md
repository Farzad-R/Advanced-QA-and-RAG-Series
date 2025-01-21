# LangGraph_1o1_Agentic_Customer_Support

## Overview
LangGraph_1o1_Agentic_Customer_Support is a project designed to demonstrate how complex systems can be built using LangGraph. In this project, we create an agentic customer service chatbot for Swiss Airlines in four different versions, addressing common real-world challenges at each step. The system supports a wide range of tasks through 18 tools, including Retrieval-Augmented Generation (RAG), web search, and travel planning.

## Features
- **Customer History:** Automatically fetch historical data
- **Web Search:** Provide additional information via web searches
- **RAG:** Answer inquiries based on company policies
- **Flights:** Search, update, and cancel flight tickets
- **Car Rentals:** Search, book, update, and cancel car rentals
- **Hotels:** Search, book, update, and cancel hotel reservations
- **Excursions:** Search, book, update, and cancel excursions

## Setup Instructions for Linux users
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/dreamboat26/Advanced-QA-and-RAG-Series.git
   cd  LangGraph_1o1_Agentic_Customer_Support
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure API Keys:**
   Edit the `.env` file and add:
   ```
   OPEN_AI_API_KEY=...
   TAVILY_API_KEY=...
   LANGCHAIN_API_KEY=...
   ```

6. **download and prepare the SQL database and the vector database**
   ```bash
   python data_preparation/download_data.py
   python data_preparation/prepare_vector_db.py
   ```

7. **Run the User Interface:**
   ```bash
   python src/app.py
   ```

8. **Configure Project Settings:**
   Modify `config/config.yml` as needed.

9. **Refresh the database after testing:**
   ```bash
   python data_preparation/update_db_date.py
   ```

## Technologies
- **Programming Language:** Python
- **Language Models:** OpenAI GPT models
- **Agents Framework:** LangGraph
- **Monitoring System:** LangSmith
- **User Interface:** Gradio
- **Database Interaction:** SQLAlchemy

## Documentation
For detailed tool descriptions, the database report, and system design schema, refer to the `documentation` folder.
