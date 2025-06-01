import os
from pyprojroot import here
from yaml import load, Loader
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()


class LoadConfig:
    def __init__(self):
        with open(here("config/config.yml"), "r") as f:
            config = load(f, Loader=Loader)
        # directories
        self.data_directory = str(
            here(config["directories"]["data_directory"]))
        self.stored_vectordb_dir = str(
            here(config["directories"]["vectordb_dir"]))

        # llm_config
        self.rag_llm = init_chat_model(
            config["model_config"]["rag_model"], model_provider=config["model_config"]["model_provider"])
        self.chat_llm = init_chat_model(
            config["model_config"]["chat_llm"], model_provider=config["model_config"]["model_provider"])
        self.chat_llm_system_message = config["model_config"]["chat_llm_system_message"]
        self.temperature = config["model_config"]["temperature"]
        self.embedding_model = config["model_config"]["embedding_model"]
        self.embeddings = OpenAIEmbeddings(
            model=config["model_config"]["embedding_model"])

        self.max_recursion = config["summarizer"]["max_recursion"]
        # rag_config
        self.collection_name = config["rag_config"]["collection_name"]

        self.k = config["rag_config"]["k"]
        self.chunk_size = config["rag_config"]["chunk_size"]
        self.chunk_overlap = config["rag_config"]["chunk_overlap"]

        # Load API keys
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

        self.stored_vectordb = Chroma(
            persist_directory=self.stored_vectordb_dir,
            embedding_function=self.embeddings
        )
        self.db_uri = config["databases"]["db_uri"]
