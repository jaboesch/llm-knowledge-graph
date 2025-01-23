from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from graph_reader_agent.state import OverallState
from log_manager import log
from graph_reader_agent.utils import parse_function
from prompt_manager import ATOMIC_FACT_CHECK_PROMPT, ATOMIC_FACT_CHECK_ARG_UPDATED_NOTEBOOK, ATOMIC_FACT_CHECK_ARG_RATIONAL_NEXT_ACTION, ATOMIC_FACT_CHECK_ARG_CHOSEN_ACTION

class AtomicFactOutput(BaseModel):
    updated_notebook: str = Field(description=ATOMIC_FACT_CHECK_ARG_UPDATED_NOTEBOOK)
    rational_next_action: str = Field(description=ATOMIC_FACT_CHECK_ARG_RATIONAL_NEXT_ACTION)
    chosen_action: str = Field(description=ATOMIC_FACT_CHECK_ARG_CHOSEN_ACTION)

class AtomicFactCheck:
    def __init__(self, chat_model, db_context):
        self.chat_model = chat_model
        self.db_context = db_context

    def __call__(self, state: OverallState) -> OverallState:
        prompt = ChatPromptTemplate.from_messages([
            ("system", ATOMIC_FACT_CHECK_PROMPT),
            ("human", """
Question: {question}
Plan: {rational_plan}
Previous actions: {previous_actions}
Notebook: {notebook}
Atomic facts: {atomic_facts}"""),
        ])
        chain = prompt | self.chat_model.with_structured_output(AtomicFactOutput)

        log(f"Check Atomic Facts Queue: {state.get('check_atomic_facts_queue')}")
        atomic_facts = self.db_context.get_atomic_facts(state.get("check_atomic_facts_queue"))
        result = chain.invoke({
            "question": state.get("question"),
            "rational_plan": state.get("rational_plan"),
            "notebook": state.get("notebook"),
            "previous_actions": state.get("previous_actions"),
            "atomic_facts": atomic_facts,
        })

        chosen_action = parse_function(result.chosen_action)
        log(f"Chosen Action: {chosen_action}")

        response = {
            "notebook": result.updated_notebook,
            "chosen_action": chosen_action.get("function_name"),
            "check_atomic_facts_queue": [],
            "previous_actions": [f"atomic_fact_check({state.get('check_atomic_facts_queue')})"],
        }
        
        if chosen_action.get("function_name") == "stop_and_read_neighbor":
            neighbors = self.db_context.get_neighbors_by_key_element(state.get("check_atomic_facts_queue"))
            response["neighbor_check_queue"] = neighbors
        elif chosen_action.get("function_name") == "read_chunk":
            response["check_chunks_queue"] = chosen_action.get("arguments")[0]
        return response