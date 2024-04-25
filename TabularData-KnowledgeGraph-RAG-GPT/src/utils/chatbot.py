from typing import List, Tuple
from utils.load_config import LoadConfig
from langchain.schema import SystemMessage, HumanMessage
import langchain
langchain.debug = True

APPCFG = LoadConfig()


class ChatBot:
    """
    Class representing a chatbot with the ability to query the Neo4j GrapDB.

    This class provides a static method for responding to user queries.
    """
    @staticmethod
    def respond(chatbot: List, message: str, chatbot_functionality: str) -> Tuple:
        if chatbot_functionality == "Q&A with GraphDB":
            chain_response = APPCFG.chain.invoke({"query": message})
            response = chain_response["result"]

        elif chatbot_functionality == "RAG with GraphDB":
            embeddings = APPCFG.client.embeddings.create(
                input=message,
                model=APPCFG.embedding_model_name
            )
            question_embedding = embeddings.data[0].embedding
            search_result = APPCFG.graph.query("""
                with $question_embedding as question_embedding
                CALL db.index.vector.queryNodes(
                    'movie_tagline_embeddings', 
                    $top_k, 
                    question_embedding
                    ) YIELD node AS movie, score
                RETURN movie.title, movie.tagline, score
                """,
                                               params={
                                                   "question_embedding": question_embedding,
                                                   "top_k": APPCFG.top_k
                                               })
            messages = [
                SystemMessage(
                    content=(
                        APPCFG.system_message
                    )
                ),
                HumanMessage(
                    content=f"User question:\n{message}\n\n"+f"Search result:\n{str(search_result)}")
            ]
            response = APPCFG.llm(messages)

        chatbot.append((message, response))
        return "", chatbot
