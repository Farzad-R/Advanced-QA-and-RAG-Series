import os
from typing import List, Tuple
from dotenv import load_dotenv
from pyprojroot import here
import yaml
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

with open(here("configs/config.yml")) as cfg:
    APP_CONFIG = yaml.load(cfg, Loader=yaml.FullLoader)


class HydeRAG:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=APP_CONFIG["embedding_model"])
        self.llm = ChatOpenAI(model=APP_CONFIG["hyde_rag"]["llm_model"],
                              temperature=APP_CONFIG["hyde_rag"]["temperature"])
        self.logs = []
        self.retrievers = {}
        self._setup_retrievers()
        self._setup_hyde_generator()

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

    def _setup_hyde_generator(self):
        """Setup hypothetical document generator"""

        # Dataset-specific HyDE templates
        self.hyde_templates = {
            "tech_docs": """You are a technical documentation expert. Write a comprehensive explanation that would appear in technical documentation about: '{query}' Generate a response that is less than 500 words long.

                            Your response should be detailed, technical, and include:
                            - Key concepts and definitions
                            - How it works or is implemented
                            - Common use cases or applications
                            - Technical specifications or features

                            Write as if this is from an authoritative technical source.""",

            "faq_data": """You are a customer service expert. Write a detailed FAQ answer that would appear in a company's help documentation for: '{query}' Generate a response that is less than 500 words long.

                            Your response should be practical and include:
                            - Direct answer to the question
                            - Step-by-step instructions if applicable
                            - Policy details or requirements
                            - Common variations or related concerns

                            Write as if this is from an official company FAQ.""",

            "news_articles": """You are a technology news journalist. Write a comprehensive news article that would appear in a tech publication about: '{query}' Generate a response that is less than 500 words long.

                            Your response should be informative and include:
                            - Current developments or trends
                            - Key facts and statistics
                            - Industry impact or implications
                            - Expert insights or analysis

                            Write as if this is from a reputable technology news source."""
        }

        # Create HyDE chain
        self.hyde_chain = self.llm | StrOutputParser()

    def _log(self, message: str):
        """Enhanced logging with visual separators"""
        log_entry = f"HYDE RAG: {message}"
        self.logs.append(log_entry)

        # Add visual separator after key steps
        if any(step in message for step in ["Step", "HyDE Generation:"]):
            self.logs.append("     |")
            self.logs.append("     |")
            self.logs.append("     V")

    def _generate_hypothetical_document(self, query: str, dataset: str) -> str:
        """Generate hypothetical document based on query and dataset type"""

        self._log(
            "HyDE Generation: Creating hypothetical document for improved retrieval")

        # Select appropriate template based on dataset
        template = self.hyde_templates.get(
            dataset, self.hyde_templates["tech_docs"])

        try:
            # Create prompt
            prompt = ChatPromptTemplate.from_template(template)

            # Generate hypothetical document
            hyde_chain = prompt | self.llm | StrOutputParser()
            hypothetical_doc = hyde_chain.invoke({"query": query})

            # Log the hypothetical document (truncated for readability)
            doc_preview = hypothetical_doc[:300] if hypothetical_doc else "No content"
            self._log(f"Generated HyDE document: '{doc_preview}...'")

            return hypothetical_doc

        except Exception as e:
            self._log(f"HyDE generation failed: {str(e)}")
            # Fallback to original query if HyDE fails
            return query

    def _retrieve_with_hyde(self, hypothetical_doc: str, dataset: str) -> List:
        """Retrieve documents using the hypothetical document as search query"""

        self._log("HyDE Retrieval: Searching with generated hypothetical document")

        if dataset not in self.retrievers:
            self._log(f"Dataset {dataset} not available")
            return []

        retriever = self.retrievers[dataset]

        # Use hypothetical document for retrieval instead of original query
        documents = retriever.get_relevant_documents(
            hypothetical_doc, k=APP_CONFIG["hyde_rag"]["hypothetical_doc_retrieval_top_k"])

        self._log(
            f"HyDE Retrieval: Found {len(documents)} documents using hypothetical embedding")

        return documents

    def process_query(self, query: str, dataset: str) -> Tuple[str, List[str]]:
        self.logs = []  # Clear logs
        self._log("Starting HyDE RAG pipeline")

        try:
            if dataset not in self.retrievers:
                return f"Dataset {dataset} not available", self.logs

            self._log(f"Original Query: '{query[:60]}...'")

            # Step 1: Generate hypothetical document
            hypothetical_doc = self._generate_hypothetical_document(
                query, dataset)

            # Step 2: Retrieve using hypothetical document
            documents = self._retrieve_with_hyde(hypothetical_doc, dataset)

            if not documents:
                self._log(
                    "Fallback: No documents found with HyDE, trying direct query")
                # Fallback to direct retrieval if HyDE fails
                retriever = self.retrievers[dataset]
                documents = retriever.get_relevant_documents(
                    query, k=APP_CONFIG["hyde_rag"]["direct_retrieval_top_k"])
                self._log(
                    f"Fallback retrieval: Found {len(documents)} documents")

            # Step 3: Generate response using retrieved documents
            self._log("Step 2: Generating response with HyDE-enhanced context")

            template = """Answer the question based on the retrieved context:

                        {context}

                        Original Question: {question}

                        Provide a comprehensive answer using the context. The context was retrieved using an advanced hypothetical document matching technique for better relevance.

                        Answer:"""

            prompt = ChatPromptTemplate.from_template(template)

            def format_docs(docs):
                if not docs:
                    self._log("Context: No documents available")
                    return "No relevant documents found."

                total_chars = sum(len(doc.page_content)
                                  for doc in docs if doc.page_content)
                self._log(
                    f"Context: Using {len(docs)} HyDE-retrieved documents ({total_chars} chars)")
                return "\n\n".join(doc.page_content for doc in docs if doc.page_content)

            rag_chain = (
                {"context": lambda x: format_docs(
                    documents), "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )

            response = rag_chain.invoke(query)

            self._log(
                "Completed: HyDE RAG generated response using hypothetical document retrieval")

            return response, self.logs

        except Exception as e:
            error_msg = f"HyDE RAG failed: {str(e)}"
            self._log(error_msg)
            return f"Error processing request: {str(e)}", self.logs
