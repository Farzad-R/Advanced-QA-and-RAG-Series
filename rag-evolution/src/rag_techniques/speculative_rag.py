from typing import List, Tuple
from pyprojroot import here
import random
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import chromadb
from langchain.schema import Document
from src.load_config import APPConfig

APP_CONFIG = APPConfig().load()


class SpeculativeRAG:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=APP_CONFIG.embedding_model)
        self.drafter_llm = ChatOpenAI(
            # For generating drafts
            model=APP_CONFIG.speculative_rag.drafter_llm_model,
            temperature=APP_CONFIG.speculative_rag.drafter_temperature
        )
        # Lower temp for consistent scoring
        self.verifier_llm = ChatOpenAI(
            model=APP_CONFIG.speculative_rag.verifier_llm_model,
            temperature=APP_CONFIG.speculative_rag.verifier_temperature
        )
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

                    def get_relevant_documents(self, query: str, k: int = 6):
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

    def _setup_generators(self):
        """Setup draft and verification generators with STRICT scoring"""

        # Draft generation prompt
        self.draft_prompt = ChatPromptTemplate.from_template("""
Based on the provided evidence, answer the question comprehensively.

Evidence:
{evidence}

Question: {question}

Provide a detailed answer based on the evidence above. Be thorough and accurate.

Answer:""")

        # FIXED: Much more critical verification prompt
        self.verification_prompt = ChatPromptTemplate.from_template("""
                    You are a STRICT verification agent. Evaluate this answer critically and assign a harsh but fair score.

                    Evidence Available:
                    {evidence}

                    Question: {question}

                    Proposed Answer:
                    {answer}

                    STRICT EVALUATION CRITERIA:
                    - Score 9-10: EXCEPTIONAL - Completely accurate, uses ALL relevant evidence, perfectly structured, no gaps
                    - Score 7-8: GOOD - Mostly accurate, uses most evidence well, minor issues or missed opportunities  
                    - Score 5-6: ADEQUATE - Partially accurate, uses some evidence, has noticeable gaps or errors
                    - Score 3-4: POOR - Limited accuracy, minimal evidence use, significant problems
                    - Score 1-2: VERY POOR - Inaccurate, doesn't use evidence well, major errors

                    CHECK FOR THESE ISSUES (deduct points):
                    - Missing key information from evidence (-1 to -3 points)
                    - Inaccurate statements not supported by evidence (-2 to -4 points)
                    - Poor organization or unclear explanations (-1 to -2 points)
                    - Repetitive or redundant content (-1 point)
                    - Doesn't fully answer the question asked (-2 to -3 points)
                    - Generic statements that could apply to any topic (-1 to -2 points)

                    IMPORTANT: Most answers have flaws. Be critical. Scores of 9-10 should be rare and only for truly exceptional responses.

                    Provide ONLY the numerical score (1-10):""")

        # Additional verification prompt for detailed scoring
        self.detailed_verification_prompt = ChatPromptTemplate.from_template("""
                        You are evaluating this answer across multiple dimensions. Be critical and specific.

                        Evidence: {evidence}
                        Question: {question}
                        Answer: {answer}

                        Rate each dimension (1-10) and explain briefly:

                        ACCURACY: How factually correct is the answer?
                        COMPLETENESS: How well does it address all aspects of the question?
                        EVIDENCE_USE: How effectively does it incorporate the provided evidence?
                        CLARITY: How clear and well-organized is the response?

                        Format your response as:
                        ACCURACY: [score] - [brief reason]
                        COMPLETENESS: [score] - [brief reason]
                        EVIDENCE_USE: [score] - [brief reason]
                        CLARITY: [score] - [brief reason]
                        OVERALL: [average score]""")

    def _log(self, message: str):
        """Enhanced logging with visual separators"""
        log_entry = f"SPECULATIVE RAG: {message}"
        self.logs.append(log_entry)

        # Add visual separator after key steps
        if any(step in message for step in ["Sampling:", "Drafting:", "Verification:", "Selection:"]):
            self.logs.append("     |")
            self.logs.append("     |")
            self.logs.append("     V")

    def _multi_perspective_sampling(self, documents: List, k: int = 3) -> List[List]:
        """Create multiple document subsets from different perspectives"""

        self._log(
            f"Sampling: Creating {k} different document perspectives from {len(documents)} total documents")

        if len(documents) < k:
            # If we have fewer documents than desired perspectives, create overlapping subsets
            subsets = []
            for i in range(k):
                subset = documents.copy()
                random.shuffle(subset)
                subsets.append(subset)
            return subsets

        # Create different subsets by sampling documents
        subsets = []
        doc_texts = [doc.page_content for doc in documents]

        # Method 1: Sequential chunks
        chunk_size = max(2, len(documents) // k)
        for i in range(0, min(len(documents), k * chunk_size), chunk_size):
            subset = doc_texts[i:i + chunk_size]
            if subset:  # Only add non-empty subsets
                subsets.append(subset)

        # Method 2: Random sampling for additional perspectives
        while len(subsets) < k and len(documents) > 1:
            sample_size = min(len(documents), max(2, len(documents) // 2))
            subset = random.sample(doc_texts, sample_size)
            subsets.append(subset)

        # Ensure we have exactly k subsets
        while len(subsets) < k:
            subsets.append(random.sample(doc_texts, min(len(doc_texts), 2)))

        self._log(
            f"Sampling: Generated {len(subsets)} document subsets with sizes: {[len(s) for s in subsets]}")
        return subsets[:k]

    def _generate_draft_response(self, query: str, evidence_subset: List[str]) -> str:
        """Generate a draft response using a subset of evidence"""

        try:
            evidence_text = "\n\n".join(
                [f"[{i+1}] {doc}" for i, doc in enumerate(evidence_subset)])

            draft_chain = self.draft_prompt | self.drafter_llm | StrOutputParser()

            draft = draft_chain.invoke({
                "evidence": evidence_text,
                "question": query
            })

            return draft

        except Exception as e:
            return f"Error generating draft: {str(e)}"

    def _verify_response(self, query: str, evidence_subset: List[str], draft: str, draft_index: int) -> Tuple[float, str]:
        """Verify and score a draft response with detailed feedback and forced differentiation"""

        try:
            evidence_text = "\n\n".join(
                [f"[{i+1}] {doc}" for i, doc in enumerate(evidence_subset)])

            # Create differentiated prompts for each draft to force variation
            differentiation_prompts = [
                "Focus especially on factual accuracy and evidence support. Be extra critical of any unsupported claims.",
                "Focus especially on completeness and depth. Penalize heavily if the answer doesn't fully address all aspects of the question.",
                "Focus especially on clarity and organization. Be particularly harsh on verbose or poorly structured responses."
            ]

            # Use different verification approach for each draft
            verification_prompt_with_focus = ChatPromptTemplate.from_template("""
                        You are a STRICT verification agent with a specific focus area. {focus_instruction}

                        Evidence Available:
                        {evidence}

                        Question: {question}

                        Proposed Answer:
                        {answer}

                        STRICT EVALUATION CRITERIA:
                        - Score 9-10: EXCEPTIONAL - Near perfect, exceptional quality in your focus area
                        - Score 7-8: GOOD - Solid quality but noticeable room for improvement in your focus area  
                        - Score 5-6: ADEQUATE - Acceptable but clear deficiencies in your focus area
                        - Score 3-4: POOR - Significant problems in your focus area
                        - Score 1-2: VERY POOR - Major failures in your focus area

                        Your focus: {focus_instruction}

                        CHECK FOR THESE SPECIFIC ISSUES:
                        - Missing key information from evidence (-2 to -4 points)
                        - Inaccurate or unsupported statements (-3 to -5 points)
                        - Poor organization or unclear explanations (-1 to -3 points)
                        - Doesn't fully answer the question (-2 to -4 points)
                        - Generic or superficial content (-1 to -3 points)

                        Be HARSH. Most answers should score 4-7. Only truly exceptional answers deserve 8+.
                        Provide ONLY the numerical score (1-10):""")

            focus_instruction = differentiation_prompts[draft_index % len(
                differentiation_prompts)]

            verify_chain = verification_prompt_with_focus | self.verifier_llm | StrOutputParser()

            score_text = verify_chain.invoke({
                "evidence": evidence_text,
                "question": query,
                "answer": draft,
                "focus_instruction": focus_instruction
            })

            # Extract score and add small random variation to break ties
            try:
                base_score = float(score_text.strip().split()[0])
                # Add small random variation (-0.3 to +0.3) to differentiate identical scores
                variation = (random.random() - 0.5) * 0.6
                final_score = base_score + variation
                final_score = max(1.0, min(10.0, final_score))

                self._log(
                    f"Draft {draft_index + 1} focus: {focus_instruction[:50]}...")
                self._log(
                    f"Draft {draft_index + 1} base score: {base_score}, with variation: {final_score:.1f}")

                return final_score, score_text
            except:
                # Fallback with variation
                fallback_score = 5.0 + \
                    (random.random() - 0.5) * 2.0  # 4.0 to 6.0 range
                return max(1.0, min(10.0, fallback_score)), score_text

        except Exception as e:
            self._log(f"Verification error: {str(e)}")
            error_score = 4.0 + (random.random() - 0.5) * \
                2.0  # 3.0 to 5.0 for errors
            return error_score, f"Error during verification: {str(e)}"

    def process_query(self, query: str, dataset: str) -> Tuple[str, List[str]]:
        self.logs = []  # Clear logs
        self._log(
            "Starting Speculative RAG pipeline with parallel generation and STRICT verification")

        try:
            if dataset not in self.retrievers:
                return f"Dataset {dataset} not available", self.logs

            # Step 1: Retrieve documents
            self._log("Step 1: Retrieving documents from knowledge base")
            retriever = self.retrievers[dataset]
            documents = retriever.get_relevant_documents(
                # Get more docs for better sampling
                query, k=APP_CONFIG.speculative_rag.top_k)

            if not documents:
                self._log("No documents retrieved")
                return "I couldn't find relevant documents to answer your question.", self.logs

            self._log(
                f"Retrieved {len(documents)} documents for multi-perspective sampling")

            # Step 2: Multi-perspective sampling
            k_perspectives = 3  # Number of different perspectives
            document_subsets = self._multi_perspective_sampling(
                documents, k=k_perspectives)

            # Step 3: Parallel draft generation
            self._log("Drafting: Generating multiple draft responses in parallel")
            drafts = []

            for i, subset in enumerate(document_subsets):
                draft = self._generate_draft_response(query, subset)
                drafts.append(draft)
                self._log(
                    f"Draft {i+1}: Generated response using {len(subset)} documents ({len(draft)} chars)")

            # Step 4: STRICT parallel verification
            self._log(
                "Verification: CRITICALLY evaluating quality of each draft response")
            scores = []
            detailed_feedback = []

            for i, (draft, subset) in enumerate(zip(drafts, document_subsets)):
                score, feedback = self._verify_response(
                    query, subset, draft, i)
                scores.append(score)
                detailed_feedback.append(feedback)
                self._log(
                    f"Draft {i+1}: STRICT quality score = {score:.1f}/10")

            # Step 5: Select best response
            best_index = scores.index(max(scores))
            best_score = scores[best_index]
            best_response = drafts[best_index]

            self._log(
                f"Selection: Chose Draft {best_index + 1} with highest score ({best_score:.1f}/10)")
            self._log(
                f"Completed: Speculative RAG generated {len(drafts)} candidates and selected the best response")

            # Log score distribution for debugging
            score_dist = f"Score distribution: {[f'{s:.1f}' for s in scores]}"
            self._log(f"Debug: {score_dist}")

            return best_response, self.logs

        except Exception as e:
            error_msg = f"Speculative RAG failed: {str(e)}"
            self._log(error_msg)
            return f"Error processing request: {str(e)}", self.logs
