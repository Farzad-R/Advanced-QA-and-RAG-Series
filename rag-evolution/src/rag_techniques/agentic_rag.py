import os
from typing import List, Tuple, Dict, Any
from dotenv import load_dotenv
from pyprojroot import here
import yaml
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

with open(here("configs/config.yml")) as cfg:
    APP_CONFIG = yaml.load(cfg, Loader=yaml.FullLoader)


class AgenticRAG:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=APP_CONFIG["embedding_model"])
        self.llm = ChatOpenAI(model=APP_CONFIG["corrective_rag"]["llm_model"],
                              temperature=APP_CONFIG["corrective_rag"]["temperature"])
        self.logs = []
        self.retrievers = {}
        self._setup_retrievers()
        self._setup_agents()

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

    def _setup_agents(self):
        """Setup specialized agents"""
        self.planning_agent = self.llm
        self.research_agent = self.llm
        self.synthesis_agent = self.llm
        self.tool_agent = self.llm

    def _log(self, message: str):
        """Enhanced logging with visual separators"""
        log_entry = f"AGENTIC RAG: {message}"
        self.logs.append(log_entry)

        # Add visual separator after key steps
        if any(step in message for step in ["Agent:", "Planning:", "Research:", "Synthesis:", "Tool:"]):
            self.logs.append("     |")
            self.logs.append("     |")
            self.logs.append("     V")

    def _detect_query_characteristics(self, query: str) -> Dict[str, bool]:
        """Detect query characteristics using rule-based approach"""

        query_lower = query.lower()

        # Temporal indicators
        temporal_words = ["recent", "latest", "current",
                          "today", "now", "new", "upcoming", "2024", "2025"]
        has_temporal = any(word in query_lower for word in temporal_words)

        # Complexity indicators
        complexity_words = ["compare", "difference", "vs",
                            "versus", "how do", "what are", "analyze", "evaluate"]
        is_complex = any(word in query_lower for word in complexity_words) or len(
            query.split()) > 8

        # Cross-domain indicators
        domain_keywords = {
            "tech": ["technology", "software", "programming", "ai", "machine learning", "devops"],
            "business": ["business", "customer", "support", "practices", "operations", "expectations"],
            "current": ["developments", "trends", "changes", "impact", "evolution"]
        }

        domains_detected = []
        for domain, keywords in domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                domains_detected.append(domain)

        is_cross_domain = len(domains_detected) > 1

        return {
            "temporal": has_temporal,
            "complex": is_complex,
            "cross_domain": is_cross_domain,
            "domains": domains_detected
        }

    def _planning_agent(self, query: str, dataset: str) -> Dict[str, Any]:
        """Enhanced Planning Agent with rule-based + LLM analysis"""

        self._log("Agent: Planning Agent analyzing query characteristics")

        # Rule-based analysis
        characteristics = self._detect_query_characteristics(query)

        # Determine strategy based on characteristics
        if characteristics["temporal"] and characteristics["cross_domain"]:
            plan_type = "comprehensive"
            self._log(
                "Planning: Comprehensive research needed - temporal + cross-domain query")
            steps = ["local_research", "cross_dataset_search",
                     "web_search", "synthesis"]

        elif characteristics["cross_domain"]:
            plan_type = "multi_source"
            self._log(
                "Planning: Multi-source research needed - cross-domain query")
            steps = ["local_research", "cross_dataset_search", "synthesis"]

        elif characteristics["temporal"]:
            plan_type = "current_focused"
            self._log(
                "Planning: Current information focus - temporal query detected")
            steps = ["local_research", "web_search", "synthesis"]

        elif characteristics["complex"]:
            plan_type = "complex"
            self._log("Planning: Complex analysis needed - multi-faceted query")
            steps = ["local_research", "supplementary_search", "synthesis"]

        else:
            plan_type = "simple"
            self._log(
                "Planning: Simple query detected - direct retrieval approach")
            steps = ["local_research", "synthesis"]

        return {
            "type": plan_type,
            "characteristics": characteristics,
            "steps": steps
        }

    def _research_agent(self, query: str, dataset: str, plan: Dict) -> List[Dict]:
        """Enhanced Research Agent with comprehensive information gathering"""

        self._log(
            "Agent: Research Agent executing comprehensive information gathering")

        research_results = []

        # Always do primary local research
        if "local_research" in plan["steps"]:
            self._log(
                "Research: Gathering primary information from local database")
            if dataset in self.retrievers:
                retriever = self.retrievers[dataset]
                documents = retriever.get_relevant_documents(
                    query, k=APP_CONFIG["agentic_rag"]["top_k"])

                if documents:
                    self._log(
                        f"Research: Found {len(documents)} primary documents in {dataset}")
                    research_results.append({
                        "source": "primary",
                        "dataset": dataset,
                        "documents": documents,
                        "quality": "primary"
                    })

        # Cross-dataset search for multi-source/comprehensive plans
        if "cross_dataset_search" in plan["steps"]:
            self._log("Research: Cross-dataset search for comprehensive coverage")

            other_datasets = [d for d in ["tech_docs",
                                          "faq_data", "news_articles"] if d != dataset]

            for other_dataset in other_datasets:
                if other_dataset in self.retrievers:
                    other_retriever = self.retrievers[other_dataset]
                    other_docs = other_retriever.get_relevant_documents(
                        query, k=APP_CONFIG["agentic_rag"]["other_retrieval_top_k"])

                    if other_docs:
                        self._log(
                            f"Research: Found {len(other_docs)} cross-domain documents in {other_dataset}")
                        research_results.append({
                            "source": "cross_domain",
                            "dataset": other_dataset,
                            "documents": other_docs,
                            "quality": "supplementary"
                        })

        # Supplementary search for complex queries
        elif "supplementary_search" in plan["steps"]:
            self._log("Research: Supplementary search for complex query support")

            other_datasets = [d for d in ["tech_docs",
                                          "faq_data", "news_articles"] if d != dataset]

            # Limited supplementary search
            for other_dataset in other_datasets[:1]:
                if other_dataset in self.retrievers:
                    other_retriever = self.retrievers[other_dataset]
                    other_docs = other_retriever.get_relevant_documents(
                        query, k=APP_CONFIG["agentic_rag"]["other_retrieval_top_k"])

                    if other_docs:
                        self._log(
                            f"Research: Found {len(other_docs)} supplementary documents in {other_dataset}")
                        research_results.append({
                            "source": "supplementary",
                            "dataset": other_dataset,
                            "documents": other_docs,
                            "quality": "secondary"
                        })

        # Web search for temporal/current queries
        if "web_search" in plan["steps"]:
            self._log(
                "Research: Current information needed - requesting web search")
            web_info = self._tool_agent(query)
            if web_info:
                research_results.append({
                    "source": "web",
                    "content": web_info,
                    "quality": "current"
                })

        return research_results

    def _tool_agent(self, query: str) -> str:
        """Tool Agent: Handle web search and external tools"""

        self._log("Agent: Tool Agent performing web search for current information")

        try:
            from openai import OpenAI
            client = OpenAI()

            response = client.responses.create(
                model="gpt-4o-mini",
                tools=[{
                    "type": "web_search_preview",
                    "search_context_size": "low"
                }],
                input=f"Current information about: {query[:35]}"
            )

            web_content = response.output_text

            # Limit content size
            if len(web_content) > 350:
                web_content = web_content[:350] + "..."

            self._log(
                f"Tool: Retrieved {len(web_content)} chars from web search")
            return web_content

        except Exception as e:
            self._log(f"Tool Agent error: {str(e)}")
            return "Current web information not available"

    def _synthesis_agent(self, query: str, research_results: List[Dict]) -> str:
        """Enhanced Synthesis Agent with comprehensive information integration"""

        self._log("Agent: Synthesis Agent combining comprehensive research results")

        if not research_results:
            self._log("Synthesis: No research results to synthesize")
            return "I couldn't find relevant information to answer your question."

        # Categorize and prepare context from all sources
        context_parts = []
        sources_used = []
        source_categories = {"primary": 0,
                             "cross_domain": 0, "supplementary": 0, "web": 0}

        for result in research_results:
            if "documents" in result:
                docs_text = "\n".join(
                    [doc.page_content for doc in result["documents"]])

                if result["source"] == "primary":
                    context_parts.append(
                        f"Primary source ({result['dataset']}): {docs_text}")
                    source_categories["primary"] += len(result["documents"])
                elif result["source"] == "cross_domain":
                    context_parts.append(
                        f"Cross-domain source ({result['dataset']}): {docs_text}")
                    source_categories["cross_domain"] += len(
                        result["documents"])
                else:
                    context_parts.append(
                        f"Supplementary source ({result['dataset']}): {docs_text}")
                    source_categories["supplementary"] += len(
                        result["documents"])

                sources_used.append(result["dataset"])

            elif result["source"] == "web":
                context_parts.append(
                    f"Current information: {result['content']}")
                sources_used.append("web search")
                source_categories["web"] = 1

        full_context = "\n\n".join(context_parts)
        sources_list = ", ".join(set(sources_used))

        # Enhanced logging with source breakdown
        source_summary = []
        for category, count in source_categories.items():
            if count > 0:
                source_summary.append(f"{count} {category}")

        self._log(
            f"Synthesis: Combining information from sources: {sources_list}")
        self._log(f"Synthesis: Source breakdown: {', '.join(source_summary)}")

        # Enhanced synthesis prompt
        synthesis_prompt = """You are a Synthesis Agent. Create a comprehensive, well-structured answer using the provided information from multiple sources.

Context from research:
{context}

Question: {question}

Instructions:
- Provide a complete answer that directly addresses the question
- Integrate information from multiple sources when available
- Highlight insights that come from combining different sources
- Maintain clarity while being comprehensive
- Note if you're drawing from current/recent information

Answer:"""

        try:
            prompt = ChatPromptTemplate.from_template(synthesis_prompt)
            synthesis_chain = prompt | self.synthesis_agent | StrOutputParser()

            response = synthesis_chain.invoke({
                "context": full_context,
                "question": query
            })

            self._log("Synthesis: Generated comprehensive multi-source response")
            return response

        except Exception as e:
            self._log(f"Synthesis Agent error: {str(e)}")
            return "Error generating response from available information."

    def process_query(self, query: str, dataset: str) -> Tuple[str, List[str]]:
        self.logs = []  # Clear logs
        self._log(
            "Starting Agentic RAG pipeline with robust multi-agent coordination")

        try:
            # Step 1: Enhanced Planning Agent
            plan = self._planning_agent(query, dataset)

            # Step 2: Comprehensive Research Agent
            research_results = self._research_agent(query, dataset, plan)

            # Step 3: Enhanced Synthesis Agent
            response = self._synthesis_agent(query, research_results)

            # Calculate detailed statistics
            total_docs = 0
            source_details = []
            web_sources = 0

            for result in research_results:
                if "documents" in result:
                    doc_count = len(result["documents"])
                    total_docs += doc_count
                    source_details.append(f"{result['dataset']}: {doc_count}")
                elif result["source"] == "web":
                    web_sources = 1

            sources_summary = ", ".join(source_details)
            if web_sources:
                sources_summary += ", web search: 1" if sources_summary else "web search: 1"

            info_sources = len(research_results)
            self._log(
                f"Completed: Used {total_docs + web_sources} information pieces from {info_sources} sources ({sources_summary})")

            return response, self.logs

        except Exception as e:
            error_msg = f"Agentic RAG failed: {str(e)}"
            self._log(error_msg)
            return f"Error processing request: {str(e)}", self.logs
