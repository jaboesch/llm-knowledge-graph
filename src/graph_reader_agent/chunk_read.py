from typing import Dict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from graph_reader_agent.state import OverallState
from log_manager import log
from graph_reader_agent.utils import parse_function
from prompt_manager import CHUNK_READ_PROMPT, CHUNK_READ_ARG_UPDATED_NOTEBOOK, CHUNK_READ_ARG_RATIONAL_NEXT_ACTION, CHUNK_READ_ARG_CHOSEN_ACTION

class ChunkOutput(BaseModel):
    updated_notebook: str = Field(description=CHUNK_READ_ARG_UPDATED_NOTEBOOK)
    rational_next_action: str = Field(description=CHUNK_READ_ARG_RATIONAL_NEXT_ACTION)
    chosen_action: str = Field(description=CHUNK_READ_ARG_CHOSEN_ACTION)

class ChunkRead:
    def __init__(self, chat_model, embeddings_model, db_context):
        self.chat_model = chat_model
        self.embeddings_model = embeddings_model
        self.db_context = db_context

    def __call__(self, state: OverallState) -> OverallState:
        prompt = ChatPromptTemplate.from_messages([
            ("system", CHUNK_READ_PROMPT),
            ("human", """
Question: {question}
Plan: {rational_plan}
Previous actions: {previous_actions}
Notebook: {notebook}
Chunk: {chunk}"""),
        ])
        chain = prompt | self.chat_model.with_structured_output(ChunkOutput)

        check_chunks_queue = state.get("check_chunks_queue")
        chunk_id = check_chunks_queue.pop()
        chunk_text = self.db_context.get_node_by_id(chunk_id)
        result = chain.invoke({
            "question": state.get("question"),
            "rational_plan": state.get("rational_plan"),
            "notebook": state.get("notebook"),
            "previous_actions": state.get("previous_actions"),
            "chunk": chunk_text,
        })
        
        chosen_action = parse_function(result.chosen_action)
        log(
            f"Rational for next action after reading chunks: {result.rational_next_action}"
        )
        log(f"Chosen action: {chosen_action}")

        response = {
            "notebook": result.updated_notebook,
            "chosen_action": chosen_action.get("function_name"),
            "previous_actions": [f"read_chunk([{chunk_id}])"],
        }
        if chosen_action.get("function_name") == "read_subsequent_chunk":
            subsequent_id = self.db_context.get_subsequent_chunk_id(chunk_id)
            check_chunks_queue.append(subsequent_id)
        elif chosen_action.get("function_name") == "read_previous_chunk":
            previous_id = self.db_context.get_previous_chunk_id(chunk_id)
            check_chunks_queue.append(previous_id)
        elif chosen_action.get("function_name") == "search_more":
            # Go over to next chunk
            # Else explore neighbors
            if not check_chunks_queue:
                response["chosen_action"] = "search_neighbor"
                # Get neighbors/use vector similarity
                log(f"Neighbor rational: {result.rational_next_action}")
                embeddings = self.embeddings_model.embed_query(result.rational_next_action)
                neighbors = self.db_context.get_similar_nodes(embeddings)
                response["neighbor_check_queue"] = neighbors

        response["check_chunks_queue"] = check_chunks_queue
        return response