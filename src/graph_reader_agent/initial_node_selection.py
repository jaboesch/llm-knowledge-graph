from typing import List
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from graph_reader_agent.state import OverallState
from prompt_manager import (
    INITIAL_NODE_PROMPT,
    INITIAL_NODE_ARG_KEY_ELEMENT,
    INITIAL_NODE_ARG_SCORE,
)
from log_manager import log


class Node(BaseModel):
    key_element: str = Field(description=INITIAL_NODE_ARG_KEY_ELEMENT)
    score: int = Field(description=INITIAL_NODE_ARG_SCORE)


class InitialNodes(BaseModel):
    initial_nodes: List[Node] = Field(
        description="List of relevant nodes to the question and plan."
    )


class InitialNodeSelection:
    def __init__(self, chat_model, embeddings_model, db_context):
        self.chat_model = chat_model
        self.embeddings_model = embeddings_model
        self.db_context = db_context

    def __call__(self, state: OverallState) -> OverallState:
        initial_node_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    INITIAL_NODE_PROMPT,
                ),
                (
                    "human",
                    (
                        """Question: {question}
Plan: {rational_plan}
Nodes: {nodes}"""
                    ),
                ),
            ]
        )

        initial_nodes_chain = (
            initial_node_prompt | self.chat_model.with_structured_output(InitialNodes)
        )
        # get embeddings of the question and plan
        embeddings = self.embeddings_model.embed_query(state.get("question"))
        potential_nodes = self.db_context.get_similar_nodes(embeddings)
        
        inputs = {
            "question": state.get("question"),
            "rational_plan": state.get("rational_plan"),
            "nodes": potential_nodes,
        }
        
        initial_nodes = initial_nodes_chain.invoke(inputs)
        # paper uses 5 initial nodes
        check_atomic_facts_queue = [
            el.key_element
            for el in sorted(
                initial_nodes.initial_nodes,
                key=lambda node: node.score,
                reverse=True,
            )
        ][:5]
        return {
            "check_atomic_facts_queue": check_atomic_facts_queue,
            "previous_actions": ["initial_node_selection"],
        }
