import os
from typing import List, Tuple
from utils.load_config import LoadConfig
from sqlalchemy import create_engine, inspect
import pandas as pd
APPCFG = LoadConfig()


class ProcessFiles:
    """
    A class to process uploaded files, converting them to a SQL database format.

    This class handles both CSV and XLSX files, reading them into pandas DataFrames and
    storing each as a separate table in the SQL database specified by the application configuration.
    """
    def __init__(self, files_dir: List, chatbot: List) -> None:
        """
        Initialize the ProcessFiles instance.

        Args:
            files_dir (List): A list containing the file paths of uploaded files.
            chatbot (List): A list representing the chatbot's conversation history.
        """
        APPCFG = LoadConfig()
        self.files_dir = files_dir
        self.chatbot = chatbot
        db_path = APPCFG.uploaded_files_sqldb_directory
        db_path = f"sqlite:///{db_path}"
        self.engine = create_engine(db_path)
        print("Number of uploaded files:", len(self.files_dir))

    def _process_uploaded_files(self) -> Tuple:
        """
        Private method to process the uploaded files and store them into the SQL database.

        Returns:
            Tuple[str, List]: A tuple containing an empty string and the updated chatbot conversation list.
        """
        for file_dir in self.files_dir:
            file_names_with_extensions = os.path.basename(file_dir)
            file_name, file_extension = os.path.splitext(
                file_names_with_extensions)
            if file_extension == ".csv":
                df = pd.read_csv(file_dir)
            elif file_extension == ".xlsx":
                df = pd.read_excel(file_dir)
            else:
                raise ValueError("The selected file type is not supported")
            df.to_sql(file_name, self.engine, index=False)
        print("==============================")
        print("All csv/xlsx files are saved into the sql database.")
        self.chatbot.append(
            (" ", "Uploaded files are ready. Please ask your question"))
        return "", self.chatbot

    def _validate_db(self):
        """
        private method to validate that the SQL database has been updated correctly with the right tables.
        """
        insp = inspect(self.engine)
        table_names = insp.get_table_names()
        print("==============================")
        print("Available table nasmes in created SQL DB:", table_names)
        print("==============================")

    def run(self):
        """
        public method to execute the file processing pipeline.

        Includes steps for processing uploaded files and validating the database.

        Returns:
            Tuple[str, List]: A tuple containing an empty string and the updated chatbot conversation list.
        """
        input_txt, chatbot = self._process_uploaded_files()
        self._validate_db()
        return input_txt, chatbot


class UploadFile:
    """
    A class that acts as a controller to run various file processing pipelines
    based on the chatbot's current functionality when handling uploaded files.
    """
    @staticmethod
    def run_pipeline(files_dir: List, chatbot: List, chatbot_functionality: str):
        """
        Run the appropriate pipeline based on chatbot functionality.

        Args:
            files_dir (List): List of paths to uploaded files.
            chatbot (List): The current state of the chatbot's dialogue.
            chatbot_functionality (str): A string specifying the chatbot's current functionality.

        Returns:
            Tuple: A tuple of an empty string and the updated chatbot list, or None if functionality not matched.
        """
        if chatbot_functionality == "Process files":
            pipeline_instance = ProcessFiles(
                files_dir=files_dir, chatbot=chatbot)
            input_txt, chatbot = pipeline_instance.run()
            return input_txt, chatbot
        else:
            pass # Other functionalities can be implemented here.
