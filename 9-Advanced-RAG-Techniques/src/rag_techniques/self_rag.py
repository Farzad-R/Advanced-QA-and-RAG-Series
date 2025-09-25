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


class SelfRAG:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=APP_CONFIG["embedding_model"])
        self.llm = ChatOpenAI(model=APP_CONFIG["self_rag"]["llm_model"],
                              temperature=APP_CONFIG["self_rag"]["temperature"])
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
        """Setup self-reflection grading models"""

        # Document relevance grader
        class GradeDocuments(BaseModel):
            """Binary score for relevance check on retrieved documents."""
            binary_score: str = Field(
                description="Documents are relevant to the question, 'yes' or 'no'"
            )

        # Hallucination grader
        class GradeHallucinations(BaseModel):
            """Binary score for hallucination present in generation answer."""
            binary_score: str = Field(
                description="Answer is grounded in the facts, 'yes' or 'no'"
            )

        # Answer quality grader
        class GradeAnswer(BaseModel):
            """Binary score to assess answer addresses question."""
            binary_score: str = Field(
                description="Answer addresses the question, 'yes' or 'no'"
            )

        # Setup grading chains
        self.doc_grader_llm = self.llm.with_structured_output(GradeDocuments)
        self.hallucination_grader_llm = self.llm.with_structured_output(
            GradeHallucinations)
        self.answer_grader_llm = self.llm.with_structured_output(GradeAnswer)

        # Document grading prompt
        doc_grade_system = """You are a grader assessing relevance of retrieved documents to a user question.

            If the document contains ANY concepts, keywords, or topics related to the question, grade it as relevant.
            The goal is to keep potentially useful information, and filter out irrelevant information.
            Only filter out documents that are completely unrelated to the topic.

            Give a binary score 'yes' or 'no'."""

        self.doc_grade_prompt = ChatPromptTemplate.from_messages([
            ("system", doc_grade_system),
            ("human",
             "Retrieved document: \n\n {document} \n\n User question: {question}")
        ])

        self.doc_grader = self.doc_grade_prompt | self.doc_grader_llm

        # Hallucination grading prompt
        hallucination_system = """You are a grader assessing whether an LLM generation is grounded in / supported by retrieved facts.

                Give a binary score 'yes' or 'no'. 'Yes' means the answer is grounded in the facts.
                The answer should be more focused on the topic and retrieved facts and less general."""

        self.hallucination_prompt = ChatPromptTemplate.from_messages([
            ("system", hallucination_system),
            ("human",
             "Set of facts: \n\n {documents} \n\n LLM generation: {generation}")
        ])

        self.hallucination_grader = self.hallucination_prompt | self.hallucination_grader_llm

        # Answer quality grading prompt
        answer_system = """You are a grader assessing whether an answer addresses / resolves a question.

        Give a binary score 'yes' or 'no'. 'Yes' means the answer resolves the question."""

        self.answer_prompt = ChatPromptTemplate.from_messages([
            ("system", answer_system),
            ("human",
             "User question: \n\n {question} \n\n LLM generation: {generation}")
        ])

        self.answer_grader = self.answer_prompt | self.answer_grader_llm

        # Query rewriter for retries
        rewrite_system = """You are a question re-writer that converts an input question to a better version optimized for vectorstore retrieval.

                            Look at the input and reason about the underlying semantic intent/meaning.
                            The goal is to improve the question to be more specific and relevant to the topic.
                            The question should be more focused on the topic and less general.
                           """

        self.rewrite_prompt = ChatPromptTemplate.from_messages([
            ("system", rewrite_system),
            ("human",
             "Here is the initial question: \n\n {question} \n Formulate an improved question.")
        ])

        self.query_rewriter = self.rewrite_prompt | self.llm | StrOutputParser()

    def _log(self, message: str):
        """Enhanced logging with visual separators"""
        log_entry = f"SELF-RAG: {message}"
        self.logs.append(log_entry)

        # Add visual separator after key steps
        if any(step in message for step in ["Step", "Self-Reflection:", "Retry"]):
            self.logs.append("     |")
            self.logs.append("     |")
            self.logs.append("     V")

    def _grade_documents(self, question: str, documents: List) -> Tuple[List, bool]:
        """Self-reflection: Grade document relevance and determine if retry needed"""
        if not documents:
            return [], True

        self._log(
            f"Self-Reflection: Grading {len(documents)} retrieved documents for relevance")

        relevant_docs = []
        for i, doc in enumerate(documents):
            try:
                score = self.doc_grader.invoke({
                    "question": question,
                    "document": doc.page_content
                })

                if score.binary_score.lower() == "yes":
                    relevant_docs.append(doc)
                    self._log(
                        f"Document {i+1}: RELEVANT - keeping for generation")
                else:
                    self._log(f"Document {i+1}: NOT RELEVANT - filtering out")

            except Exception as e:
                self._log(f"Document {i+1}: Grading failed - {str(e)}")

        # Decision logic for retry
        total_docs = len(documents)
        relevant_count = len(relevant_docs)
        failed_count = total_docs - relevant_count

        # If 2 or more fail (out of 3), trigger retry
        need_retry = failed_count >= 2

        self._log(
            f"Document filtering: {relevant_count}/{total_docs} documents passed relevance check")

        if need_retry:
            self._log(
                "Self-Reflection: Too many documents failed - will trigger query rewrite")
        else:
            self._log(
                "Self-Reflection: Sufficient documents passed - proceeding with generation")

        return relevant_docs, need_retry

    def _generate_response(self, question: str, documents: List) -> str:
        """Generate response using filtered documents"""

        template = """Answer the question based on the following context:

                        {context}

                        Question: {question}

                        Provide a comprehensive and accurate answer based on the context.

                        Answer:"""

        prompt = ChatPromptTemplate.from_template(template)

        def format_docs(docs):
            if not docs:
                return "No relevant documents found."
            return "\n\n".join(doc.page_content for doc in docs if doc.page_content)

        context = format_docs(documents)

        rag_chain = (
            {"context": lambda x: context, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        return rag_chain.invoke(question)

    def _self_reflect_on_generation(self, question: str, documents: List, generation: str) -> Tuple[bool, bool]:
        """Self-reflection: Check if generation is grounded and addresses question"""

        self._log("Self-Reflection: Evaluating generated response quality")

        # Check for hallucinations
        try:
            doc_text = "\n".join([doc.page_content for doc in documents])
            hallucination_score = self.hallucination_grader.invoke({
                "documents": doc_text,
                "generation": generation
            })
            is_grounded = hallucination_score.binary_score.lower() == "yes"

            if is_grounded:
                self._log(
                    "Hallucination check: PASSED - response is grounded in facts")
            else:
                self._log(
                    "Hallucination check: FAILED - response contains unsupported claims")

        except Exception as e:
            self._log(f"Hallucination check failed: {str(e)}")
            is_grounded = False

        # Check if answer addresses the question
        try:
            answer_score = self.answer_grader.invoke({
                "question": question,
                "generation": generation
            })
            addresses_question = answer_score.binary_score.lower() == "yes"

            if addresses_question:
                self._log(
                    "Question relevance check: PASSED - response addresses the question")
            else:
                self._log(
                    "Question relevance check: FAILED - response doesn't address the question")

        except Exception as e:
            self._log(f"Answer relevance check failed: {str(e)}")
            addresses_question = False

        return is_grounded, addresses_question

    def process_query(self, query: str, dataset: str) -> Tuple[str, List[str]]:
        self.logs = []  # Clear logs
        self._log("Starting Self-RAG pipeline with self-reflection mechanisms")

        max_retries = 2
        current_query = query

        try:
            if dataset not in self.retrievers:
                return f"Dataset {dataset} not available", self.logs

            retriever = self.retrievers[dataset]

            for attempt in range(max_retries + 1):
                if attempt > 0:
                    self._log(
                        f"Retry {attempt}: Attempting improved retrieval and generation")

                # Step 1: Retrieve documents
                self._log("Step 1: Initial document retrieval")
                documents = retriever.get_relevant_documents(
                    current_query, k=APP_CONFIG["self_rag"]["top_k"])
                self._log(
                    f"Retrieved {len(documents)} documents from {dataset}")

                # Step 2: Self-reflection on documents
                relevant_docs, need_retry = self._grade_documents(
                    current_query, documents)

                # Adaptive threshold: be more lenient on final attempt
                if need_retry and attempt == max_retries and relevant_docs:
                    # On final attempt, accept any relevant documents found
                    self._log(
                        "Self-Reflection: Final attempt - accepting available relevant documents")
                    need_retry = False

                if need_retry:
                    if attempt < max_retries:
                        self._log(
                            "Self-Reflection: Document quality insufficient - rewriting query for retry")
                        current_query = self.query_rewriter.invoke(
                            {"question": current_query})
                        self._log(
                            f"Rewritten query: '{current_query[:60]}...'")
                        continue
                    else:
                        self._log(
                            "Self-Reflection: Max retries reached with insufficient documents")
                        return "I couldn't find sufficient relevant information to answer your question reliably.", self.logs

                # Step 3: Generate response
                self._log("Step 2: Generating response with relevant documents")
                generation = self._generate_response(
                    current_query, relevant_docs)

                # Step 4: Self-reflection on generation
                is_grounded, addresses_question = self._self_reflect_on_generation(
                    query, relevant_docs, generation  # Use original query for final check
                )

                # Step 5: Decide whether to accept or retry
                if is_grounded and addresses_question:
                    self._log(
                        "Self-Reflection: Response quality approved - accepting answer")
                    self._log(
                        "Completed: Self-RAG generated high-quality response with self-reflection")
                    return generation, self.logs

                elif attempt < max_retries:
                    if not is_grounded:
                        self._log(
                            "Self-Reflection: Response not grounded - retrying generation")
                    if not addresses_question:
                        self._log(
                            "Self-Reflection: Response doesn't address question - rewriting query")
                        current_query = self.query_rewriter.invoke(
                            {"question": current_query})
                    continue
                else:
                    self._log(
                        "Self-Reflection: Max retries reached - returning best available response")
                    self._log(
                        "Completed: Self-RAG completed with quality concerns noted")
                    return generation, self.logs

        except Exception as e:
            error_msg = f"Self-RAG failed: {str(e)}"
            self._log(error_msg)
            return f"Error processing request: {str(e)}", self.logs
