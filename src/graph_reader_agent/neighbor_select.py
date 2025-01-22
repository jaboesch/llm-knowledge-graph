from typing import Dict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from graph_reader_agent.state import OverallState
from log_manager import log
from graph_reader_agent.utils import parse_function
from prompt_manager import NEIGHBOR_SELECT_PROMPT, NEIGHBOR_SELECT_ARG_RATIONAL_NEXT_ACTION, NEIGHBOR_SELECT_ARG_CHOSEN_ACTION

class NeighborOutput(BaseModel):
    rational_next_action: str = Field(description=NEIGHBOR_SELECT_ARG_RATIONAL_NEXT_ACTION)
    chosen_action: str = Field(description=NEIGHBOR_SELECT_ARG_CHOSEN_ACTION)

class NeighborSelect:
    def __init__(self, chat_model, db_context):
        self.chat_model = chat_model
        self.db_context = db_context

    def __call__(self, state: OverallState) -> OverallState:
        prompt = ChatPromptTemplate.from_messages([
            ("system", NEIGHBOR_SELECT_PROMPT),
            ("human", """
Question: {question}
Plan: {rational_plan}
Previous actions: {previous_actions}
Notebook: {notebook}
Neighbor nodes: {nodes}"""),
        ])
        chain = prompt | self.chat_model.with_structured_output(NeighborOutput)

        neighbors = state.get("neighbor_check_queue")
        result = chain.invoke({
            "question": state.get("question"),
            "rational_plan": state.get("rational_plan"),
            "notebook": state.get("notebook"),
            "previous_actions": state.get("previous_actions"),
            "nodes": neighbors,
        })

        log(
            f"Rational for next action after selecting neighbor: {result.rational_next_action}"
        )
        chosen_action = parse_function(result.chosen_action)
        log(f"Chosen action: {chosen_action}")
        # Empty neighbor select queue
        response = {
            "chosen_action": chosen_action.get("function_name"),
            "neighbor_check_queue": [],
            "previous_actions": [
                f"neighbor_select({chosen_action.get('arguments', [''])[0] if chosen_action.get('arguments', ['']) else ''})"
            ],
        }
        if chosen_action.get("function_name") == "read_neighbor_node":
            response["check_atomic_facts_queue"] = [chosen_action.get("arguments")[0]]
        return response