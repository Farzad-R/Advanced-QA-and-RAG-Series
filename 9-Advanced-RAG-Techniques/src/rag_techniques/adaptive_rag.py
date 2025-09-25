import os
from typing import List, Tuple, Literal
from dotenv import load_dotenv
from pyprojroot import here
import yaml
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

with open(here("configs/config.yml")) as cfg:
    APP_CONFIG = yaml.load(cfg, Loader=yaml.FullLoader)


class AdaptiveRAG:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=APP_CONFIG["embedding_model"])
        self.llm = ChatOpenAI(
            model=APP_CONFIG["adaptive_rag"]["llm_model"],
            temperature=APP_CONFIG["adaptive_rag"]["temperature"]
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
        """Setup document relevance graders"""

        # Data models for structured output
        class RouteQuery(BaseModel):
            """Route a user query to the most appropriate strategy."""
            strategy: Literal["standard", "multi_retrieval", "rewrite"] = Field(
                ...,
                description="Choose retrieval strategy: standard for simple queries, multi_retrieval for complex queries, rewrite for unclear queries"
            )

        class GradeDocuments(BaseModel):
            """Binary score for relevance check on retrieved documents."""
            binary_score: str = Field(
                description="Documents are relevant to the question, 'yes' or 'no'"
            )

        # Route query LLM
        self.query_router_llm = self.llm.with_structured_output(RouteQuery)

        # Document grader LLM
        self.doc_grader_llm = self.llm.with_structured_output(GradeDocuments)

        # Route prompt
        route_system = """You are an expert at determining the best retrieval strategy for different types of queries.

                    Available strategies:
                    - standard: Simple, direct questions with clear intent (e.g., "What is Python?", "How does shipping work?")
                    - multi_retrieval: Complex questions requiring multiple pieces of information (e.g., "Compare X and Y", "What are pros and cons?")  
                    - rewrite: Vague or unclear questions that need clarification (e.g., "How does it work?", "Tell me more about that")

                    Choose the best strategy based on query complexity and clarity."""

        self.route_prompt = ChatPromptTemplate.from_messages([
            ("system", route_system),
            ("human", "{question}")
        ])

        self.query_router = self.route_prompt | self.query_router_llm

        # Document grading prompt
        grade_system = """You are a grader assessing relevance of retrieved documents to a user question.

                If the document contains ANY concepts related to the question, grade it as relevant.
                The goal is to keep potentially useful documents and filter out irrelevant documents.
                Only filter out documents that are completely unrelated to the topic.
                Give a binary score 'yes' or 'no'."""

        self.grade_prompt = ChatPromptTemplate.from_messages([
            ("system", grade_system),
            ("human",
             "Retrieved document: \n\n {document} \n\n User question: {question}")
        ])

        self.doc_grader = self.grade_prompt | self.doc_grader_llm

        # Query rewriter
        rewrite_system = """You are a query rewriter that converts unclear or vague questions into clearer, more specific questions optimized for retrieval.
        
                        Look at the input question and improve it by:
                        - Adding context if missing
                        - Making vague terms more specific  
                        - Clarifying ambiguous references
                        - Maintaining the original intent"""

        self.rewrite_prompt = ChatPromptTemplate.from_messages([
            ("system", rewrite_system),
            ("human",
             "Here is the initial question: \n\n {question} \n Formulate an improved question.")
        ])

        self.query_rewriter = self.rewrite_prompt | self.llm | StrOutputParser()

    def _log(self, message: str):
        """Enhanced logging with visual separators"""
        log_entry = f"ADAPTIVE RAG: {message}"
        self.logs.append(log_entry)

        # Add visual separator after key steps
        if any(step in message for step in ["Strategy:", "Step", "Decision:"]):
            self.logs.append("     |")
            self.logs.append("     |")
            self.logs.append("     V")

    def _route_query(self, query: str) -> str:
        """Route query to appropriate strategy"""
        self._log("Route Analysis: Determining optimal retrieval strategy")

        route_result = self.query_router.invoke({"question": query})
        strategy = route_result.strategy

        strategy_descriptions = {
            "standard": "Standard retrieval for clear, direct questions",
            "multi_retrieval": "Multi-step retrieval for complex queries",
            "rewrite": "Query rewriting for unclear or vague questions"
        }

        self._log(
            f"Strategy: Selected '{strategy}' - {strategy_descriptions[strategy]}")
        return strategy

    def _grade_documents(self, query: str, documents: List) -> List:
        """Grade document relevance and filter out irrelevant docs"""
        if not documents:
            return documents

        self._log(
            f"Document Grading: Evaluating {len(documents)} retrieved documents")

        relevant_docs = []
        for i, doc in enumerate(documents):
            score = self.doc_grader.invoke({
                "question": query,
                "document": doc.page_content
            })

            if score.binary_score == "yes":
                relevant_docs.append(doc)
                self._log(f"✓ Document {i+1}: Relevant")
            else:
                self._log(f"✗ Document {i+1}: Not relevant - filtered out")

        self._log(
            f"Filtering Results: {len(relevant_docs)}/{len(documents)} documents passed relevance check")
        return relevant_docs

    def _rewrite_query(self, query: str) -> str:
        """Rewrite unclear queries for better retrieval"""
        self._log("Query Rewriting: Improving unclear query for better retrieval")

        rewritten = self.query_rewriter.invoke({"question": query})
        self._log(f"Original: '{query[:60]}...'")
        self._log(f"Rewritten: '{rewritten[:60]}...'")

        return rewritten

    def _standard_retrieval(self, query: str, dataset: str) -> List:
        """Standard single-pass retrieval"""
        self._log("Step 1: Standard retrieval - single similarity search")
        retriever = self.retrievers[dataset]
        docs = retriever.get_relevant_documents(
            query, k=APP_CONFIG["adaptive_rag"]["standard_retrieval_top_k"])
        self._log(
            f"Retrieved {len(docs)} documents using standard similarity search")
        return docs

    def _multi_retrieval(self, query: str, dataset: str) -> List:
        """Multi-step retrieval for complex queries"""
        self._log("Step 1: Multi-step retrieval - expanding search strategy")

        # First retrieval
        retriever = self.retrievers[dataset]
        docs1 = retriever.get_relevant_documents(
            query, k=APP_CONFIG["adaptive_rag"]["multi_retrieval_first_top_k"])
        self._log(f"Initial retrieval: {len(docs1)} documents")

        # Generate alternative query formulations for complex topics
        alt_query_prompt = f"Alternative ways to search for: {query}"
        docs2 = retriever.get_relevant_documents(
            alt_query_prompt, k=APP_CONFIG["adaptive_rag"]["multi_retrieval_second_top_k"])
        self._log(f"Alternative search: {len(docs2)} additional documents")

        # Combine and deduplicate
        all_docs = docs1 + docs2
        unique_docs = []
        seen_content = set()

        for doc in all_docs:
            if doc.page_content not in seen_content:
                unique_docs.append(doc)
                seen_content.add(doc.page_content)

        self._log(
            f"Combined results: {len(unique_docs)} unique documents after deduplication")
        return unique_docs

    def process_query(self, query: str, dataset: str) -> Tuple[str, List[str]]:
        self.logs = []  # Clear logs
        self._log("Starting Adaptive RAG pipeline")

        try:
            if dataset not in self.retrievers:
                return f"Dataset {dataset} not available", self.logs

            # Step 1: Route query to determine strategy
            strategy = self._route_query(query)

            # Step 2: Execute retrieval based on strategy
            if strategy == "rewrite":
                # Rewrite query first, then use standard retrieval
                improved_query = self._rewrite_query(query)
                documents = self._standard_retrieval(improved_query, dataset)
            elif strategy == "multi_retrieval":
                documents = self._multi_retrieval(query, dataset)
            else:  # standard
                documents = self._standard_retrieval(query, dataset)

            # Step 3: Grade and filter documents
            filtered_docs = self._grade_documents(query, documents)

            # Step 4: Adaptive decision making
            if not filtered_docs:
                self._log(
                    "Decision: No relevant documents found - trying query rewrite as fallback")
                if strategy != "rewrite":  # Avoid infinite loop
                    improved_query = self._rewrite_query(query)
                    documents = self._standard_retrieval(
                        improved_query, dataset)
                    filtered_docs = self._grade_documents(
                        improved_query, documents)

            # Step 5: Generate response
            self._log(
                "Step 2: Generating adaptive response with filtered context")

            template = """Answer the question based on this carefully selected context:

                    {context}

                    Question: {question}

                    Provide a comprehensive answer using the most relevant information from the context. If the context doesn't fully address the question, acknowledge the limitations.

                    Answer:"""

            prompt = ChatPromptTemplate.from_template(template)

            def format_docs(docs):
                if not docs:
                    self._log("Context: No relevant documents available")
                    return "No relevant documents found."

                total_chars = sum(len(doc.page_content)
                                  for doc in docs if doc.page_content)
                self._log(
                    f"Context: Using {len(docs)} filtered documents ({total_chars} chars)")
                return "\n\n".join(doc.page_content for doc in docs if doc.page_content)

            rag_chain = (
                {"context": lambda x: format_docs(
                    filtered_docs), "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )

            response = rag_chain.invoke(query)

            # Final summary
            self._log(
                f"Completed: Adaptive RAG with {strategy} strategy successfully processed query")

            return response, self.logs

        except Exception as e:
            error_msg = f"Adaptive RAG failed: {str(e)}"
            self._log(error_msg)
            return f"Error processing request: {str(e)}", self.logs
