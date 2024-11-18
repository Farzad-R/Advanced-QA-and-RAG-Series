import os
from dotenv import load_dotenv
import yaml
from pyprojroot import here
from langchain_openai import ChatOpenAI
load_dotenv()

with open(here("configs/config.yml")) as cfg:
    app_config = yaml.load(cfg, Loader=yaml.FullLoader)


class LoadConfig:
    def __init__(self) -> None:
        # Databases directories
        self.local_file = here(app_config["directories"]["local_file"])
        self.backup_file = here(app_config["directories"]["backup_file"])
        self.vectordb_dir = here(app_config["RAG"]["vectordb"])
        self.collection_name = str(app_config["RAG"]["collection_name"])

        os.environ['OPENAI_API_KEY'] = os.getenv("OPEN_AI_API_KEY")
        self.llm = ChatOpenAI(model=app_config["openai_models"]["model"])
        self.embedding_model = str(
            app_config["openai_models"]["embedding_model"])

        self.k = int(app_config["RAG"]["k"])

        self.tavily_search_max_results = int(
            app_config["tavily_search"]["max_results"])

        os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
        os.environ["LANGCHAIN_TRACING_V2"] = str(
            app_config["langsmith"]["tracing"])
        os.environ["LANGCHAIN_PROJECT"] = str(
            app_config["langsmith"]["project_name"])
