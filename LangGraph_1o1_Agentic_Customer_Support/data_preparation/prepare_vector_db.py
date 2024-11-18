import os
import yaml
from pyprojroot import here
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv


class PrepareVectorDB:
    """
    A class to prepare and manage a Vector Database (VectorDB) using documents from a specified directory.
    The class performs the following tasks:
    - Loads and splits documents (PDFs).
    - Splits the text into chunks based on the specified chunk size and overlap.
    - Embeds the document chunks using a specified embedding model.
    - Stores the embedded vectors in a persistent VectorDB directory.

    Attributes:
        doc_dir (str): Path to the directory containing documents (PDFs) to be processed.
        chunk_size (int): The maximum size of each chunk (in characters) into which the document text will be split.
        chunk_overlap (int): The number of overlapping characters between consecutive chunks.
        embedding_model (str): The name of the embedding model to be used for generating vector representations of text.
        vectordb_dir (str): Directory where the resulting vector database will be stored.
        collection_name (str): The name of the collection to be used within the vector database.

    Methods:
        run() -> None:
            Executes the process of reading documents, splitting text, embedding them into vectors, and 
            saving the resulting vector database. If the vector database directory already exists, it skips
            the creation process.
    """

    def __init__(self,
                 doc_dir: str,
                 chunk_size: int,
                 chunk_overlap: int,
                 embedding_model: str,
                 vectordb_dir: str,
                 collection_name: str
                 ) -> None:

        self.doc_dir = doc_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = embedding_model
        self.vectordb_dir = vectordb_dir
        self.collection_name = collection_name

    def run(self):
        """
        Executes the main logic to create and store document embeddings in a VectorDB.

        If the vector database directory doesn't exist:
        - It loads PDF documents from the `doc_dir`, splits them into chunks,
        - Embeds the document chunks using the specified embedding model,
        - Stores the embeddings in a persistent VectorDB directory.

        If the directory already exists, it skips the embedding creation process.

        Prints the creation status and the number of vectors in the vector database.

        Returns:
            None
        """
        if not os.path.exists(here(self.vectordb_dir)):
            loader = TextLoader(str(here(self.doc_dir)), encoding='UTF-8')
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
            )
            doc_splits = text_splitter.split_documents(docs)
            # If it doesn't exist, create the directory and create the embeddings
            os.makedirs(here(self.vectordb_dir))
            print(f"Directory '{self.vectordb_dir}' was created.")
            # Add to vectorDB
            vectordb = Chroma.from_documents(
                documents=doc_splits,
                collection_name=self.collection_name,
                embedding=OpenAIEmbeddings(model=self.embedding_model),
                persist_directory=str(here(self.vectordb_dir))
            )
            print("VectorDB is created and saved.")
            print("Number of vectors in vectordb:",
                  vectordb._collection.count(), "\n\n")
        else:
            print(f"Directory '{self.vectordb_dir}' already exists.")


if __name__ == "__main__":
    load_dotenv()
    os.environ['OPENAI_API_KEY'] = os.getenv("OPEN_AI_API_KEY")

    with open(here("configs/config.yml")) as cfg:
        app_config = yaml.load(cfg, Loader=yaml.FullLoader)

    # Uncomment the following configs to run for stories document
    chunk_size = int(app_config["RAG"]["chunk_size"])
    chunk_overlap = int(app_config["RAG"]["chunk_overlap"])
    embedding_model = str(app_config["RAG"]["embedding_model"])
    vectordb_dir = str(app_config["RAG"]["vectordb"])
    collection_name = str(app_config["RAG"]["collection_name"])
    doc_dir = str(app_config["RAG"]["doc_dir"])

    prepare_db_instance = PrepareVectorDB(
        doc_dir=doc_dir,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        embedding_model=embedding_model,
        vectordb_dir=vectordb_dir,
        collection_name=collection_name)

    prepare_db_instance.run()
