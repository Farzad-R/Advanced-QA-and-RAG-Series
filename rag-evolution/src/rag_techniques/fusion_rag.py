from typing import List, Tuple
from pyprojroot import here
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.load import dumps, loads
import chromadb
from langchain.schema import Document
from src.load_config import APPConfig

APP_CONFIG = APPConfig().load()


class FusionRAG:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=APP_CONFIG.embedding_model)
        self.query_generator_llm = ChatOpenAI(
            # For query generation
            model=APP_CONFIG.fusion_rag.query_generator_llm_model,
            temperature=APP_CONFIG.fusion_rag.query_generator_temperature
        )
        self.answer_generator_llm = ChatOpenAI(
            model=APP_CONFIG.fusion_rag.answer_generator_llm_model,
            temperature=APP_CONFIG.fusion_rag.answer_generator_temperature
        )  # For final answer
        self.logs = []
        self.retrievers = {}
        self._setup_retrievers()
        self._setup_generators()

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

                            return documents
                        except Exception as e:
                            self.logger(
                                f"Retrieval error for query '{query}': {str(e)}")
                            return []

                self.retrievers[dataset] = CustomRetriever(
                    collection, self.embeddings, self._log)

            except Exception as e:
                self._log(f"Setup error for {dataset}: {str(e)}")

    def _setup_generators(self):
        """Setup query generation and answer generation prompts"""

        # Enhanced query generation prompt for more diversity
        self.query_generation_prompt = ChatPromptTemplate.from_template("""
You are an expert at creating diverse search queries. Your goal is to generate queries that will retrieve different types of relevant information.

Original Query: {original_query}

Create 3 alternative queries that approach this topic from VERY DIFFERENT angles:

QUERY STRATEGIES TO USE:
1. DEFINITIONAL: Focus on "what is" or basic concepts/definitions
2. RELATIONAL: Focus on connections, relationships, or comparisons  
3. PRACTICAL: Focus on applications, examples, or implementation details
4. CONTEXTUAL: Focus on broader context, history, or implications

Make each query significantly different in:
- Keywords used
- Scope (broad vs specific)
- Perspective (technical vs practical)
- Information type sought

Format as:
1. [Alternative query with different focus]
2. [Alternative query with different angle] 
3. [Alternative query with different scope]

Generated queries:""")

        # Answer generation prompt
        self.answer_generation_prompt = ChatPromptTemplate.from_template("""
Based on the provided context documents, answer the following question comprehensively and accurately.

Context:
{context}

Question: {question}

Instructions:
- Use only the information provided in the context
- If the context doesn't contain enough information, acknowledge this limitation
- Organize your response clearly and logically
- Cite relevant information when possible

Answer:""")

    def _log(self, message: str):
        """Enhanced logging with visual separators"""
        log_entry = f"FUSION RAG: {message}"
        self.logs.append(log_entry)

        # Add visual separator after key steps
        if any(step in message for step in ["Creating different ways", "Searching through", "Combining and ranking", "Analyzing the best"]):
            self.logs.append("     |")
            self.logs.append("     |")
            self.logs.append("     V")

    def _generate_sub_queries(self, original_query: str) -> List[str]:
        """Generate multiple sub-queries from the original query"""

        try:
            self._log("Creating different ways to search for your answer")

            # Generate sub-queries
            query_chain = self.query_generation_prompt | self.query_generator_llm | StrOutputParser()

            generated_text = query_chain.invoke(
                {"original_query": original_query})

            # Parse the generated queries
            sub_queries = []
            for line in generated_text.strip().split('\n'):
                line = line.strip()
                if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                    # Remove the number prefix and clean up
                    query = line.split('.', 1)[1].strip()
                    if query.startswith('[') and query.endswith(']'):
                        query = query[1:-1]  # Remove brackets if present
                    sub_queries.append(query)

            # Add original query at the beginning
            all_queries = [original_query] + sub_queries

            self._log(
                f"Generated {len(all_queries)} different search approaches")
            for i, query in enumerate(all_queries, 1):
                self._log(f"Search approach {i}: {query}")

            return all_queries

        except Exception as e:
            self._log(f"Error creating search variations: {str(e)}")
            return [original_query]  # Fallback to original query only

    def _retrieve_for_queries(self, queries: List[str], dataset: str, k: int = 5) -> List[List]:
        """Retrieve documents for each query"""

        self._log(
            f"Searching through {dataset.replace('_', ' ')} knowledge base")

        if dataset not in self.retrievers:
            self._log(f"Dataset {dataset} not available")
            return []

        retriever = self.retrievers[dataset]
        all_results = []

        for i, query in enumerate(queries, 1):
            documents = retriever.get_relevant_documents(
                query, k=APP_CONFIG.fusion_rag.top_k)
            all_results.append(documents)
            self._log(
                f"Search approach {i} found {len(documents)} relevant documents")

        return all_results

    def _reciprocal_rank_fusion(self, results: List[List], k: int = 10) -> List:
        """Apply Reciprocal Rank Fusion to rerank documents with better discrimination"""

        self._log("Combining and ranking all search results")

        fused_scores = {}

        # Calculate RRF scores with lower k for better differentiation
        for query_idx, docs in enumerate(results):
            for rank, doc in enumerate(docs):
                doc_str = dumps(doc)
                if doc_str not in fused_scores:
                    fused_scores[doc_str] = 0

                # RRF formula with lower k for better discrimination: 1/(rank + k)
                rrf_score = 1 / (rank + k)
                fused_scores[doc_str] += rrf_score

        # Sort by fused scores (highest first)
        reranked_results = [
            (loads(doc), score)
            for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        ]

        self._log(
            f"Found {len(fused_scores)} unique documents across all searches")
        self._log(
            "Top ranked documents based on consistency across search approaches:")

        # Show top 5 results with simple RRF scores
        for i, (doc, score) in enumerate(reranked_results[:5], 1):
            content_preview = doc.page_content[:60].replace('\n', ' ')
            self._log(f"Rank {i}: (Score: {score:.3f}) {content_preview}...")

        # Return only the documents (not scores)
        return [doc for doc, score in reranked_results]

    def _generate_final_answer(self, question: str, context_docs: List, max_docs: int = 8) -> str:
        """Generate final answer using top-ranked documents"""

        self._log(
            "Analyzing the best documents to create your comprehensive answer")

        # Use top N documents for context
        top_docs = context_docs[:max_docs]

        # Prepare context
        context_text = "\n\n".join([
            f"Document {i+1}:\n{doc.page_content}"
            for i, doc in enumerate(top_docs)
        ])

        self._log(
            f"Using the top {len(top_docs)} most relevant documents for answer generation")

        # Generate answer
        try:
            answer_chain = self.answer_generation_prompt | self.answer_generator_llm | StrOutputParser()

            answer = answer_chain.invoke({
                "context": context_text,
                "question": question
            })

            self._log(f"Successfully generated comprehensive answer")
            return answer

        except Exception as e:
            error_msg = f"Error generating answer: {str(e)}"
            self._log(error_msg)
            return f"Error generating answer: {str(e)}"

    def process_query(self, query: str, dataset: str, top_k: int = 5, max_context_docs: int = 8) -> Tuple[str, List[str]]:
        """Process query using Fusion RAG approach"""

        self.logs = []  # Clear logs
        self._log(
            "Starting multi-perspective search and intelligent document fusion")

        try:
            # Step 1: Generate multiple sub-queries
            queries = self._generate_sub_queries(query)

            # Step 2: Retrieve documents for each query
            all_results = self._retrieve_for_queries(queries, dataset, k=top_k)

            if not any(all_results):
                self._log(
                    "No relevant documents found across any search approach")
                return "I couldn't find relevant documents to answer your question.", self.logs

            # Step 3: Apply RRF to rerank documents
            reranked_docs = self._reciprocal_rank_fusion(all_results)

            if not reranked_docs:
                self._log("No documents available after ranking process")
                return "I couldn't find relevant documents to answer your question.", self.logs

            # Step 4: Generate final answer
            final_answer = self._generate_final_answer(
                query, reranked_docs, max_context_docs)

            self._log(
                f"Completed: Processed {len(queries)} search approaches and analyzed {len(reranked_docs)} documents")

            return final_answer, self.logs

        except Exception as e:
            error_msg = f"Fusion RAG process failed: {str(e)}"
            self._log(error_msg)
            return f"Error processing request: {str(e)}", self.logs
