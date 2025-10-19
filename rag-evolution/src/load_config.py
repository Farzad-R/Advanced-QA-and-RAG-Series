from pathlib import Path
import yaml
import os
from pyprojroot import here
from dotenv import load_dotenv
from dataclasses import dataclass
load_dotenv()

CONFIG_PATH = here("configs/config.yml")


@dataclass
class CorrectiveRAGConfig:
    llm_model: str
    web_search_model: str
    temperature: float
    top_k: int


@dataclass
class AdaptiveRAGConfig:
    llm_model: str
    temperature: float
    standard_retrieval_top_k: int
    multi_retrieval_first_top_k: int
    multi_retrieval_second_top_k: int


@dataclass
class AgenticRAGConfig:
    llm_model: str
    temperature: float
    top_k: int
    other_retrieval_top_k: int


@dataclass
class ConversationalRAGConfig:
    llm_model: str
    temperature: float
    top_k: int


@dataclass
class FusionRAGConfig:
    query_generator_llm_model: str
    query_generator_temperature: float
    answer_generator_llm_model: str
    answer_generator_temperature: float
    top_k: int


@dataclass
class HydeRAGConfig:
    llm_model: str
    temperature: float
    hypothetical_doc_retrieval_top_k: int
    direct_retrieval_top_k: int


@dataclass
class SelfRAGConfig:
    llm_model: str
    temperature: float
    top_k: int


@dataclass
class SpeculativeRAGConfig:
    drafter_llm_model: str
    drafter_temperature: float
    verifier_llm_model: str
    verifier_temperature: float
    top_k: int


@dataclass
class StandardRAGConfig:
    llm_model: str
    temperature: float
    top_k: int


@dataclass
class APPConfig:
    chroma_db_path: str
    embedding_model: str
    corrective_rag: CorrectiveRAGConfig
    adaptive_rag: AdaptiveRAGConfig
    agentic_rag: AgenticRAGConfig
    conversational_rag: ConversationalRAGConfig
    fusion_rag: FusionRAGConfig
    hyde_rag: HydeRAGConfig
    self_rag: SelfRAGConfig
    speculative_rag: SpeculativeRAGConfig
    standard_rag: StandardRAGConfig

    def __post_init__(self):
        """Automatically set critical environment variables."""
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        else:
            print("⚠️ Warning: OPENAI_API_KEY not found in environment variables.")

    @classmethod
    def load(cls, path: str = CONFIG_PATH) -> "APPConfig":
        with open(Path(path), "r") as f:
            cfg = yaml.safe_load(f)

        return cls(
            chroma_db_path=cfg["chroma_db_path"],
            embedding_model=cfg["embedding_model"],
            corrective_rag=CorrectiveRAGConfig(**cfg["corrective_rag"]),
            adaptive_rag=AdaptiveRAGConfig(**cfg["adaptive_rag"]),
            agentic_rag=AgenticRAGConfig(**cfg["agentic_rag"]),
            conversational_rag=ConversationalRAGConfig(
                **cfg["conversational_rag"]),
            fusion_rag=FusionRAGConfig(**cfg["fusion_rag"]),
            hyde_rag=HydeRAGConfig(**cfg["hyde_rag"]),
            self_rag=SelfRAGConfig(**cfg["self_rag"]),
            speculative_rag=SpeculativeRAGConfig(**cfg["speculative_rag"]),
            standard_rag=StandardRAGConfig(**cfg["standard_rag"]),
        )

# Example usage:
# config = APPConfig.load("configs/config.yml")
# or
# config = APPConfig.load()  # uses default path
# print(config.corrective_rag.llm_model)
