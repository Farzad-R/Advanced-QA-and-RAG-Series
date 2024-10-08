from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import tool
from agent_graph.load_tools_config import LoadToolsConfig

TOOLS_CFG = LoadToolsConfig()


class SwissAirlinePolicyRAGTool:
    """
    A tool for retrieving relevant Swiss Airline policy documents using a 
    Retrieval-Augmented Generation (RAG) approach with vector embeddings.

    This tool uses a pre-trained OpenAI embedding model to transform queries into 
    vector representations. These vectors are then used to query a Chroma-based 
    vector database (persisted on disk) to retrieve the top-k most relevant 
    documents or entries from a specific collection, such as Swiss Airline policies.

    Attributes:
        embedding_model (str): The name of the OpenAI embedding model used for 
            generating vector representations of the queries.
        vectordb_dir (str): The directory where the Chroma vector database is 
            persisted on disk.
        k (int): The number of top-k nearest neighbors (most relevant documents) 
            to retrieve from the vector database.
        vectordb (Chroma): The Chroma vector database instance connected to the 
            specified collection and embedding model.

    Methods:
        __init__: Initializes the tool by setting up the embedding model, 
            vector database, and retrieval parameters.
    """

    def __init__(self, embedding_model: str, vectordb_dir: str, k: int, collection_name: str) -> None:
        """
        Initializes the SwissAirlinePolicyRAGTool with the necessary configuration.

        Args:
            embedding_model (str): The name of the embedding model (e.g., "text-embedding-ada-002")
                used to convert queries into vector representations.
            vectordb_dir (str): The directory path where the Chroma vector database is stored 
                and persisted on disk.
            k (int): The number of nearest neighbor documents to retrieve based on query similarity.
            collection_name (str): The name of the collection inside the vector database that holds 
                the Swiss Airline policy documents.
        """
        self.embedding_model = embedding_model
        self.vectordb_dir = vectordb_dir
        self.k = k
        self.vectordb = Chroma(
            collection_name=collection_name,
            persist_directory=self.vectordb_dir,
            embedding_function=OpenAIEmbeddings(model=self.embedding_model)
        )
        print("Number of vectors in vectordb:",
              self.vectordb._collection.count(), "\n\n")


@tool
def lookup_swiss_airline_policy(query: str) -> str:
    """Consult the company policies to check whether certain options are permitted."""
    rag_tool = SwissAirlinePolicyRAGTool(
        embedding_model=TOOLS_CFG.policy_rag_embedding_model,
        vectordb_dir=TOOLS_CFG.policy_rag_vectordb_directory,
        k=TOOLS_CFG.policy_rag_k,
        collection_name=TOOLS_CFG.policy_rag_collection_name)
    docs = rag_tool.vectordb.similarity_search(query, k=rag_tool.k)
    return "\n\n".join([doc.page_content for doc in docs])
