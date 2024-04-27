import os
import pandas as pd
from utils.load_config import LoadConfig
import pandas as pd


class PrepareVectorDBFromTabularData:
    """
    This class is designed to prepare a vector database from a CSV and XLSX file.
    It then loads the data into a ChromaDB collection. The process involves
    reading the CSV file, generating embeddings for the content, and storing 
    the data in the specified collection.
    
    Attributes:
        APPCFG: Configuration object containing settings and client instances for database and embedding generation.
        file_directory: Path to the CSV file that contains data to be uploaded.
    """
    def __init__(self, file_directory:str) -> None:
        """
        Initialize the instance with the file directory and load the app config.
        
        Args:
            file_directory (str): The directory path of the file to be processed.
        """
        self.APPCFG = LoadConfig()
        self.file_directory = file_directory
        
        
    def run_pipeline(self):
        """
        Execute the entire pipeline for preparing the database from the CSV.
        This includes loading the data, preparing the data for injection, injecting
        the data into ChromaDB, and validating the existence of the injected data.
        """
        self.df, self.file_name = self._load_dataframe(file_directory=self.file_directory)
        self.docs, self.metadatas, self.ids, self.embeddings = self._prepare_data_for_injection(df=self.df, file_name=self.file_name)
        self._inject_data_into_chromadb()
        self._validate_db()

    def _inject_data_into_chromadb(self):
        """
        Inject the prepared data into ChromaDB.
        
        Raises an error if the collection_name already exists in ChromaDB.
        The method prints a confirmation message upon successful data injection.
        """
        collection = self.APPCFG.chroma_client.create_collection(name=self.APPCFG.collection_name)
        collection.add(
            documents=self.docs,
            metadatas=self.metadatas,
            embeddings=self.embeddings,
            ids=self.ids
        )
        print("==============================")
        print("Data is stored in ChromaDB.")
    
    def _load_dataframe(self, file_directory: str):
        """
        Load a DataFrame from the specified CSV or Excel file.
        
        Args:
            file_directory (str): The directory path of the file to be loaded.
            
        Returns:
            DataFrame, str: The loaded DataFrame and the file's base name without the extension.
            
        Raises:
            ValueError: If the file extension is neither CSV nor Excel.
        """
        file_names_with_extensions = os.path.basename(file_directory)
        print(file_names_with_extensions)
        file_name, file_extension = os.path.splitext(
                file_names_with_extensions)
        if file_extension == ".csv":
            df = pd.read_csv(file_directory)
            return df, file_name
        elif file_extension == ".xlsx":
            df = pd.read_excel(file_directory)
            return df, file_name
        else:
            raise ValueError("The selected file type is not supported")
        

    def _prepare_data_for_injection(self, df:pd.DataFrame, file_name:str):
        """
        Generate embeddings and prepare documents for data injection.
        
        Args:
            df (pd.DataFrame): The DataFrame containing the data to be processed.
            file_name (str): The base name of the file for use in metadata.
            
        Returns:
            list, list, list, list: Lists containing documents, metadatas, ids, and embeddings respectively.
        """
        docs = []
        metadatas = []
        ids = []
        embeddings = []
        for index, row in df.iterrows():
            output_str = ""
            # Treat each row as a separate chunk
            for col in df.columns:
                output_str += f"{col}: {row[col]},\n"
            response = self.APPCFG.azure_openai_client.embeddings.create(
                input = output_str,
                model= self.APPCFG.embedding_model_name
            )
            embeddings.append(response.data[0].embedding)
            docs.append(output_str)
            metadatas.append({"source": file_name})
            ids.append(f"id{index}")
        return docs, metadatas, ids, embeddings
        

    def _validate_db(self):
        """
        Validate the contents of the database to ensure that the data injection has been successful.
        Prints the number of vectors in the ChromaDB collection for confirmation.
        """
        vectordb =  self.APPCFG.chroma_client.get_collection(name=self.APPCFG.collection_name)
        print("==============================")
        print("Number of vectors in vectordb:", vectordb.count())
        print("==============================")