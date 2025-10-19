from typing import List, Tuple, Dict
from pyprojroot import here
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import chromadb
from langchain.schema import Document
from src.load_config import APPConfig

APP_CONFIG = APPConfig().load()


class ConversationalRAG:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=APP_CONFIG.embedding_model)
        self.llm = ChatOpenAI(model=APP_CONFIG.conversational_rag.llm_model,
                              temperature=APP_CONFIG.conversational_rag.temperature)
        self.logs = []
        self.retrievers = {}
        self._setup_retrievers()

    def _setup_retrievers(self):
        """Setup retrievers for all datasets"""
        datasets = ["tech_docs", "faq_data", "news_articles"]

        for dataset in datasets:
            try:
                chroma_client = chromadb.PersistentClient(
                    path=str(here(APP_CONFIG.chroma_db_path)))
                collection = chroma_client.get_collection(dataset)

                class CustomRetriever:
                    def __init__(self, collection, embeddings, logger):
                        self.collection = collection
                        self.embeddings = embeddings
                        self.logger = logger

                    def get_relevant_documents(self, query: str, k: int = 5):
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

                            self.logger(
                                f"Retrieved {len(documents)} documents using context-aware search")
                            return documents
                        except Exception as e:
                            self.logger(f"Retrieval error: {str(e)}")
                            return []

                self.retrievers[dataset] = CustomRetriever(
                    collection, self.embeddings, self._log)

            except Exception as e:
                self._log(f"Setup error for {dataset}: {str(e)}")

    def _log(self, message: str):
        """Simple logging with conversational RAG prefix"""
        log_entry = f"CONVERSATIONAL RAG: {message}"
        self.logs.append(log_entry)

        if any(step in message for step in ["Step 1:", "Step 2:"]):
            self.logs.append("     |")
            self.logs.append("     |")
            self.logs.append("     V")

    def _format_conversation_history(self, history: List[Dict]) -> str:
        """Format conversation history for context"""
        if not history:
            return "No previous conversation."

        # Take last 5 exchanges to avoid token limit issues
        recent_history = history[-5:]
        formatted = []

        for exchange in recent_history:
            formatted.append(f"User: {exchange['user']}")
            formatted.append(f"Assistant: {exchange['assistant']}")

        return "\n".join(formatted)

    def _create_contextual_query(self, current_query: str, history: List[Dict]) -> str:
        """Create a contextual query by combining current query with relevant history"""
        if not history:
            return current_query

        # Simple approach: combine current query with last user question for better retrieval
        last_exchange = history[-1] if history else None
        if last_exchange:
            contextual_query = f"Previous context: {last_exchange['user']} Current question: {current_query}"
            self._log(
                f"Context injection: '{last_exchange['user'][:60]}...' + '{current_query[:60]}...'")
            return contextual_query

        return current_query

    def process_query(self, query: str, dataset: str, conversation_history: List[Dict] = None) -> Tuple[str, List[str]]:
        self.logs = []  # Clear logs
        self._log("Starting Conversational RAG pipeline")

        if conversation_history is None:
            conversation_history = []

        try:
            if dataset not in self.retrievers:
                return f"Dataset {dataset} not available", self.logs

            retriever = self.retrievers[dataset]

            # Log conversation memory details
            if conversation_history:
                self._log(
                    f"Memory: Loading {len(conversation_history)} previous exchanges")
                # Show snippet of recent memory
                last_exchange = conversation_history[-1]
                self._log(
                    f"Last context: User asked '{last_exchange['user'][:60]}...'")
            else:
                self._log("Memory: Starting fresh conversation (no history)")

            # Create conversational RAG prompt
            template = """You are a helpful assistant that answers questions based on the provided context and conversation history.

                            Previous Conversation:
                            {conversation_history}

                            Relevant Context:
                            {context}

                            Current Question: {question}

                            Instructions:
                            - Use the context to answer the current question
                            - Reference previous conversation when relevant
                            - If the question refers to something mentioned earlier, use that context
                            - Be conversational and maintain continuity with previous exchanges
                            - If context doesn't contain relevant information, say so clearly

                            Answer:"""

            prompt = ChatPromptTemplate.from_template(template)
            self._log(
                "Prompt: Using conversation-aware template with memory integration")

            # Create contextual query for better retrieval
            original_query = query
            contextual_query = self._create_contextual_query(
                query, conversation_history)

            # Document formatter with enhanced logging
            def format_docs(docs):
                if not docs:
                    self._log("Context: No relevant documents found")
                    return "No relevant documents found."

                total_chars = sum(len(doc.page_content)
                                  for doc in docs if doc.page_content)
                self._log(
                    f"Context: Prepared {len(docs)} docs ({total_chars} chars) with memory")
                return "\n\n".join(doc.page_content for doc in docs if doc.page_content)

            # RAG chain with conversation history
            def retrieve_and_format(inputs):
                self._log(
                    "Step 1: Retrieving documents with conversation awareness")
                docs = retriever.get_relevant_documents(
                    contextual_query, k=APP_CONFIG.conversational_rag.top_k)
                formatted = format_docs(docs)
                self._log(
                    "Step 2: Generating response with memory + retrieved context")
                return formatted

            def format_history(inputs):
                formatted = self._format_conversation_history(
                    conversation_history)
                if conversation_history:
                    self._log(
                        f"Memory: Injecting {len(conversation_history)} exchanges into prompt")
                return formatted

            rag_chain = (
                {
                    "context": retrieve_and_format,
                    "conversation_history": lambda x: format_history(x),
                    "question": RunnablePassthrough()
                }
                | prompt
                | self.llm
                | StrOutputParser()
            )

            response = rag_chain.invoke(original_query)

            # Final summary
            context_type = "with conversation memory" if conversation_history else "without memory"
            self._log(
                f"Completed: Generated contextual response {context_type}")

            return response, self.logs

        except Exception as e:
            error_msg = f"Conversational RAG failed: {str(e)}"
            self._log(error_msg)
            return f"Error processing request: {str(e)}", self.logs
