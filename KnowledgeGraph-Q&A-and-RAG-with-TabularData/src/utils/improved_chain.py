from typing import List
from langchain.chains.openai_functions import create_structured_output_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.graph_qa.cypher_utils import CypherQueryCorrector, Schema

# For step 1:
class Entities(BaseModel):
    """Identifying information about entities."""

    names: List[str] = Field(
        ...,
        description="All the person or movies appearing in the text",
    )


class PrepareImprovedAgent:
    def __init__(self, llm, graph) -> None:
        self.llm=llm
        self.graph=graph
        
    # step 1:
    def prepare_entity_chain(self):
        entity_chain_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are extracting person, movies, and years from the text.",
                ),
                (
                    "human",
                    "Use the given format to extract information from the following "
                    "input: {question}",
                ),
            ]
        )
        entity_chain = create_structured_output_chain(Entities, self.llm, entity_chain_prompt)
        return entity_chain

    # step 2:
    def map_to_database(self, values)->str:
        """
        Maps the values to entities in the database and returns the mapping information.

        Args:
            values (list): A list of values to map to entities in the database.

        Returns:
            str: A string containing the mapping information of each value to entities in the 
        """
        match_query = """MATCH (p:Person|Movie)
            WHERE p.name CONTAINS $value OR p.title CONTAINS $value
            RETURN coalesce(p.name, p.title) AS result, labels(p)[0] AS type
            LIMIT 1
            """
        result = ""
        for entity in values.names:
            response = self.graph.query(match_query, {"value": entity})
            try:
                result += f"{entity} maps to {response[0]['result']} {response[0]['type']} in database\n" # Query the database to find the mapping for the entity
            except IndexError:
                pass
        return result
    
    def prepare_cypher_prompt(self):
        # Generate Cypher statement based on natural language input
        cypher_template = """Based on the Neo4j graph schema below, write a Cypher query that would answer the user's question:
            {schema}
            Entities in the question map to the following database values:
            {entities_list}
            Question: {question}
            Cypher query:"""
        cypher_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "Given an input question, convert it to a Cypher query. No pre-amble.",
                    ),
                    ("human", cypher_template),
                ]
            )
        return cypher_prompt
    
    def prepare_cypher_response(self, entity_chain, cypher_prompt):
        cypher_response = (
            RunnablePassthrough.assign(names=entity_chain)
            | RunnablePassthrough.assign(
                entities_list=lambda x: self.map_to_database(x["names"]["function"]),
                schema=lambda _: self.graph.get_schema,
            )
            | cypher_prompt
            | self.llm.bind(stop=["\nCypherResult:"])
            | StrOutputParser()
        )
        return cypher_response
    
    def prepare_response_prompt(self):
        # Generate natural language response based on database results
        response_template = """Based on the the question, Cypher query, and Cypher response, write a natural language response:
        Question: {question}
        Cypher query: {query}
        Cypher Response: {response}"""

        response_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Given an input question and Cypher response, convert it to a natural"
                    " language answer. No pre-amble.",
                ),
                ("human", response_template),
            ]
        )
        return response_prompt

    def prepare_chain(self, cypher_response, response_prompt):
        # Cypher validation tool for relationship directions
        corrector_schema = [
            Schema(el["start"], el["type"], el["end"])
            for el in self.graph.structured_schema.get("relationships")
        ]
        cypher_validation = CypherQueryCorrector(corrector_schema)
        # variables cypher_response and llm and graph
        chain = (
            RunnablePassthrough.assign(query=cypher_response)
            | RunnablePassthrough.assign(
                response=lambda x: self.graph.query(cypher_validation(x["query"])),
            )
            | response_prompt
            | self.llm
            | StrOutputParser()
        )
        return chain
    
    def run_pipeline(self):
        entity_chain = self.prepare_entity_chain()
        cypher_prompt = self.prepare_cypher_prompt()
        cypher_response = self.prepare_cypher_response(entity_chain=entity_chain, cypher_prompt=cypher_prompt)
        response_prompt = self.prepare_response_prompt()
        chain = self.prepare_chain(cypher_response=cypher_response, response_prompt=response_prompt)
        return chain