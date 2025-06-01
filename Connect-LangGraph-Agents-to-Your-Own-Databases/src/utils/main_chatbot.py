import os
from utils.rag import run_rag
from utils.chat import run_chat
from utils.load_config import LoadConfig
from gradio import Request
from utils.logging_setup import setup_logger

logger = setup_logger("chatbot")

CFG = LoadConfig()


class MainChatbot:
    @staticmethod
    def get_response(chatbot: list, message: str, app_functionality: str, session_id: str, request: Request):
        try:
            thread_id = thread_id = f"{request.username}_session_{session_id}"
            chat_session_config = {
                "configurable": {"thread_id": thread_id}
            }

            logger.info(f"User: {request.username}, Session: {thread_id}")

            if app_functionality == "RAG":
                if not os.path.exists(CFG.stored_vectordb_dir):
                    chatbot.append(
                        (message, f"Please first create the vectorDB using `prepare_vectordb.py`."))
                    logger.info("RAG with Stored VectorDB", chatbot)
                    return "", chatbot, None
                response = run_rag(
                    message, chat_session_config)

            elif app_functionality == "Chat":
                response = run_chat(message, chat_session_config)

            chatbot.append(
                (message, response))
            return "", chatbot
        except Exception as e:
            logger.error(f"{str(e)}")
            return f"Error: {str(e)}"
