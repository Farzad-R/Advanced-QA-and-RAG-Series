
import os
from dotenv import load_dotenv
import yaml
from pyprojroot import here
from langchain.chat_models import AzureChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from openai import AzureOpenAI
from utils.improved_chain import PrepareImprovedAgent

print("Environment variables are loaded:", load_dotenv())


class LoadConfig:
    def __init__(self) -> None:
        with open(here("configs/app_config.yml")) as cfg:
            self.app_config = yaml.load(cfg, Loader=yaml.FullLoader)

        self.top_k = self.app_config["RAG_config"]["top_k"]

        # Load Azure OpenAI's GPT model
        self.load_llm_configs()
        self.load_graph_db()
        self.load_OpenAI_models_and_gpt_agent()

    def load_llm_configs(self):
        self.model_name = self.app_config["llm_config"]["model_name"]
        self.temperature = self.app_config["llm_config"]["temperature"]
        self.embedding_model_name = self.app_config["llm_config"]["embedding_model_name"]
        self.system_message = self.app_config["llm_config"]["system_message"]

    def load_graph_db(self):
        NEO4J_URI = "bolt://localhost:7687"
        NEO4J_USERNAME = "neo4j"
        NEO4J_PASSWORD = "12345678"
        NEO4J_DATABASE = 'neo4j'
        self.graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME,
                                password=NEO4J_PASSWORD, database=NEO4J_DATABASE)

    def load_OpenAI_models_and_gpt_agent(self):
        azure_openai_api_key = os.environ["OPENAI_API_KEY"]
        azure_openai_endpoint = os.environ["OPENAI_API_BASE"]
        # For the embedding model
        self.client = AzureOpenAI(
            api_key=azure_openai_api_key,
            api_version=os.environ["OPENAI_API_VERSION"],
            azure_endpoint=azure_openai_endpoint
        )
        # For the LLM
        self.llm = AzureChatOpenAI(
            openai_api_version=os.getenv("OPENAI_API_VERSION"),
            azure_deployment=self.model_name,
            model_name=self.model_name,
            temperature=self.temperature)
        self.simple_chain = GraphCypherQAChain.from_llm(
            graph=self.graph, llm=self.llm, verbose=True)
        improved_chain_instance = PrepareImprovedAgent(graph=self.graph, llm=self.llm)
        self.improved_chain = improved_chain_instance.run_pipeline()
