from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from utils.load_notebook_config import LoadConfig

CFG = LoadConfig()
# vectordb = Chroma(
#     collection_name=CFG.collection_name,
#     persist_directory=str(CFG.vectordb_dir),
#     embedding_function=OpenAIEmbeddings(model=CFG.embedding_model)
# )
# query = "Am I allowed to cancel my ticket?"
# docs = vectordb.similarity_search(query, k=CFG.k)
# test = "\n\n".join([doc.page_content for doc in docs])


@tool
def lookup_policy(query: str) -> str:
    """
    Consult the company policies to check whether certain options are permitted.
    Use this before making any flight changes performing other 'write' events.
    """
    vectordb = Chroma(
        collection_name=CFG.collection_name,
        persist_directory=str(CFG.vectordb_dir),
        embedding_function=OpenAIEmbeddings(model=CFG.embedding_model)
    )
    docs = vectordb.similarity_search(query, k=CFG.k)
    return "\n\n".join([doc.page_content for doc in docs])
