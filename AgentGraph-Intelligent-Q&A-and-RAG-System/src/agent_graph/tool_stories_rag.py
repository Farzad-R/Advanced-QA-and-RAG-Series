from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import tool
from agent_graph.load_tools_config import LoadToolsConfig

TOOLS_CFG = LoadToolsConfig()


class StoriesRAGTool:
    """
    A tool for retrieving relevant stories using a Retrieval-Augmented Generation (RAG) approach with vector embeddings.

    This tool leverages a pre-trained OpenAI embedding model to transform user queries into vector embeddings.
    It then uses these embeddings to query a Chroma-based vector database to retrieve the top-k most relevant
    stories from a specific collection stored in the database.

    Attributes:
        embedding_model (str): The name of the OpenAI embedding model used for generating vector representations of queries.
        vectordb_dir (str): The directory where the Chroma vector database is persisted on disk.
        k (int): The number of top-k nearest neighbor stories to retrieve from the vector database.
        vectordb (Chroma): The Chroma vector database instance connected to the specified collection and embedding model.

    Methods:
        __init__: Initializes the tool with the specified embedding model, vector database, and retrieval parameters.
    """

    def __init__(self, embedding_model: str, vectordb_dir: str, k: int, collection_name: str) -> None:
        """
        Initializes the StoriesRAGTool with the necessary configurations.

        Args:
            embedding_model (str): The name of the embedding model (e.g., "text-embedding-ada-002")
                used to convert queries into vector representations.
            vectordb_dir (str): The directory path where the Chroma vector database is stored and persisted on disk.
            k (int): The number of nearest neighbor stories to retrieve based on query similarity.
            collection_name (str): The name of the collection inside the vector database that holds the relevant stories.
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
def lookup_stories(query: str) -> str:
    """Search among the fictional stories and find the answer to the query. Input should be the query."""
    rag_tool = StoriesRAGTool(
        embedding_model=TOOLS_CFG.stories_rag_embedding_model,
        vectordb_dir=TOOLS_CFG.stories_rag_vectordb_directory,
        k=TOOLS_CFG.stories_rag_k,
        collection_name=TOOLS_CFG.stories_rag_collection_name)
    docs = rag_tool.vectordb.similarity_search(query, k=rag_tool.k)
    return "\n\n".join([doc.page_content for doc in docs])
