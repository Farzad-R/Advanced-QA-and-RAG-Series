import os
from typing import List, Tuple
from dotenv import load_dotenv
from pyprojroot import here
import yaml
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel, Field

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

with open(here("configs/config.yml")) as cfg:
    APP_CONFIG = yaml.load(cfg, Loader=yaml.FullLoader)


class CorrectiveRAG:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=APP_CONFIG["embedding_model"])
        self.llm = ChatOpenAI(
            model=APP_CONFIG["corrective_rag"]["llm_model"],
            temperature=APP_CONFIG["corrective_rag"]["temperature"]
        )
        self.logs = []
        self.retrievers = {}
        self._setup_retrievers()
        self._setup_graders()

    def _setup_retrievers(self):
        """Setup retrievers for all datasets"""
        datasets = ["tech_docs", "faq_data", "news_articles"]

        for dataset in datasets:
            try:
                import chromadb
                from langchain.schema import Document

                chroma_client = chromadb.PersistentClient(
                    path=str(here(APP_CONFIG["chroma_db_path"])))
                collection = chroma_client.get_collection(dataset)

                class CustomRetriever:
                    def __init__(self, collection, embeddings, logger):
                        self.collection = collection
                        self.embeddings = embeddings
                        self.logger = logger

                    def get_relevant_documents(self, query: str, k: int = 3):
                        try:
                            query_embedding = self.embeddings.embed_query(
                                query)
                            results = self.collection.query(
                                query_embeddings=[query_embedding],
                                n_results=k,
                                include=['documents', 'metadatas']
                            )

                            documents = []
                            if results['documents'] and results['documents'][0]:
                                for i, doc_content in enumerate(results['documents'][0]):
                                    metadata = results['metadatas'][0][i] if results['metadatas'][0] else {
                                    }
                                    documents.append(
                                        Document(page_content=doc_content, metadata=metadata))

                            return documents
                        except Exception as e:
                            self.logger(f"Retrieval error: {str(e)}")
                            return []

                self.retrievers[dataset] = CustomRetriever(
                    collection, self.embeddings, self._log)

            except Exception as e:
                self._log(f"Setup error for {dataset}: {str(e)}")

    def _setup_graders(self):
        """Setup document grading and query rewriting models"""

        # Document relevance grader
        class GradeDocuments(BaseModel):
            """Binary score for relevance check on retrieved documents."""
            binary_score: str = Field(
                description="Documents are relevant to the question, 'yes' or 'no'"
            )

        self.doc_grader_llm = self.llm.with_structured_output(GradeDocuments)

        # Document grading prompt
        grade_system = """You are a grader assessing relevance of retrieved documents to a user question.
        
                            If the document contains keywords or semantic meaning related to the question, grade it as relevant.
                            The goal is to filter out erroneous retrievals that don't help answer the question.
                            Give a binary score 'yes' or 'no'."""

        self.grade_prompt = ChatPromptTemplate.from_messages([
            ("system", grade_system),
            ("human",
             "Retrieved document: \n\n {document} \n\n User question: {question}")
        ])

        self.doc_grader = self.grade_prompt | self.doc_grader_llm

        # Query rewriter for better retrieval
        rewrite_system = """You are a question re-writer that converts an input question to a better version optimized for vectorstore retrieval.
        
                            Look at the input and try to reason about the underlying semantic intent/meaning.
                            Improve the question by:
                            - Making it more specific and clear
                            - Adding relevant keywords
                            - Maintaining the original intent"""

        self.rewrite_prompt = ChatPromptTemplate.from_messages([
            ("system", rewrite_system),
            ("human",
             "Here is the initial question: \n\n {question} \n Formulate an improved question.")
        ])

        self.query_rewriter = self.rewrite_prompt | self.llm | StrOutputParser()

    def _log(self, message: str):
        """Enhanced logging with visual separators"""
        log_entry = f"CORRECTIVE RAG: {message}"
        self.logs.append(log_entry)

        # Add visual separator after key steps
        if any(step in message for step in ["Step", "Decision:", "Correction:"]):
            self.logs.append("     |")
            self.logs.append("     |")
            self.logs.append("     V")

    def _web_search(self, query: str) -> str:
        """Optimized web search with token limits"""
        try:
            self._log(
                "Web Search: Using OpenAI's web search tool (minimal tokens)")

            from openai import OpenAI
            client = OpenAI()

            # Create a more focused search query
            # Limit query length
            focused_query = f"Brief summary: {query[:50]}"

            response = client.responses.create(
                model="gpt-5",
                tools=[{
                    "type": "web_search_preview",
                    "search_context_size": "low"
                }],
                input=f"Give a concise 2-sentence answer for: {focused_query}"
            )

            web_content = response.output_text

            # Truncate to maximum 500 characters to control tokens
            if len(web_content) > 2000:
                web_content = web_content[:2000] + "..."
                self._log(
                    "Web Search: Truncated results to 2000 chars for efficiency")

            self._log(
                f"Web Search: Retrieved {len(web_content)} chars from web")
            return web_content

        except Exception as e:
            self._log(f"Web Search: Failed - {str(e)}")
            return f"Current web information unavailable for: {query}"

    def _grade_documents(self, query: str, documents: List) -> Tuple[List, bool]:
        """Grade document relevance and determine if web search is needed"""
        if not documents:
            self._log("Document Grading: No documents to grade")
            return [], True

        self._log(f"Document Grading: Evaluating {len(documents)} documents")

        relevant_docs = []
        need_web_search = False

        for i, doc in enumerate(documents):
            try:
                score = self.doc_grader.invoke({
                    "question": query,
                    "document": doc.page_content
                })

                if score.binary_score.lower() == "yes":
                    relevant_docs.append(doc)
                    self._log(f"Document {i+1}: RELEVANT - keeping")
                else:
                    need_web_search = True
                    self._log(
                        f"Document {i+1}: NOT RELEVANT - will need web search")

            except Exception as e:
                self._log(f"Document {i+1}: Grading failed - {str(e)}")
                need_web_search = True

        relevance_ratio = len(relevant_docs) / len(documents)
        self._log(
            f"Document Grading: {len(relevant_docs)}/{len(documents)} relevant ({relevance_ratio:.1%})")

        # Decision logic: need web search if too few relevant docs
        if len(relevant_docs) == 0:
            self._log(
                "Decision: NO relevant documents found - web search required")
            need_web_search = True
        elif relevance_ratio < 0.5:
            self._log("Decision: LOW relevance ratio - web search recommended")
            need_web_search = True
        else:
            self._log(
                "Decision: SUFFICIENT relevant documents - no web search needed")
            need_web_search = False

        return relevant_docs, need_web_search

    def process_query(self, query: str, dataset: str) -> Tuple[str, List[str]]:
        self.logs = []  # Clear logs
        self._log("Starting Corrective RAG pipeline")

        try:
            if dataset not in self.retrievers:
                return f"Dataset {dataset} not available", self.logs

            retriever = self.retrievers[dataset]

            # Step 1: Initial retrieval
            self._log("Step 1: Initial document retrieval from local database")
            documents = retriever.get_relevant_documents(
                query, k=APP_CONFIG["corrective_rag"]["top_k"])
            self._log(f"Retrieved {len(documents)} documents from {dataset}")

            # Step 2: Grade documents and decide on web search
            relevant_docs, need_web_search = self._grade_documents(
                query, documents)

            # Step 3: Corrective action if needed
            if need_web_search:
                self._log(
                    "Correction: Insufficient relevant documents - applying corrective measures")

                # Transform query for better results
                self._log(
                    "Query Transformation: Rewriting query for better retrieval")
                improved_query = self.query_rewriter.invoke(
                    {"question": query})
                self._log(f"Original: '{query[:50]}...'")
                self._log(f"Improved: '{improved_query[:50]}...'")

                # Web search as fallback
                web_results = self._web_search(improved_query)

                # Combine web results with any relevant local docs
                if relevant_docs:
                    context = "\n\n".join(
                        [doc.page_content for doc in relevant_docs])
                    context += f"\n\n--- Additional Web Information ---\n{web_results}"
                    self._log(
                        "Context: Combined local documents + web search results")
                else:
                    context = web_results
                    self._log("Context: Using web search results only")

            else:
                # Use only local documents
                context = "\n\n".join(
                    [doc.page_content for doc in relevant_docs])
                self._log("Context: Using local documents only")

            # Step 4: Generate corrected response
            self._log(
                "Step 2: Generating corrected response with enhanced context")

            template = """Answer the question based on this context, which may include both local knowledge and web information:

                            {context}

                            Question: {question}

                            Provide a comprehensive and accurate answer. If the context includes web information, indicate this appropriately.

                            Answer:"""

            prompt = ChatPromptTemplate.from_template(template)

            rag_chain = (
                {"context": lambda x: context, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )

            response = rag_chain.invoke(query)

            # Final summary
            source_type = "corrected with web search" if need_web_search else "local documents only"
            self._log(f"Completed: Generated response using {source_type}")

            return response, self.logs

        except Exception as e:
            error_msg = f"Corrective RAG failed: {str(e)}"
            self._log(error_msg)
            return f"Error processing request: {str(e)}", self.logs
