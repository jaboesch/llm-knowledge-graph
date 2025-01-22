from graph_reader_agent.atomic_fact_check import AtomicFactCheck
from graph_reader_agent.chunk_read import ChunkRead
from graph_reader_agent.neighbor_select import NeighborSelect
from graph_reader_agent.rational_plan import RationalPlan
from graph_reader_agent.answer_reasoning import AnswerReasoning
from graph_reader_agent.initial_node_selection import InitialNodeSelection
from graph_reader_agent.state import OverallState, InputState, OutputState
from langgraph.graph import StateGraph, START, END

class GraphReaderAgent:
    def __init__(self, db_context, model_context):
        self.db_context = db_context
        self.chat_model = model_context.chat

        # Instantiate components
        self.initial_node_selection = InitialNodeSelection(model_context.chat, model_context.embeddings, db_context)
        self.rational_plan = RationalPlan(model_context.chat)
        self.atomic_fact_check = AtomicFactCheck(model_context.chat, db_context)
        self.chunk_read = ChunkRead(model_context.chat, model_context.embeddings, db_context)
        self.neighbor_select = NeighborSelect(model_context.chat, db_context)
        self.answer_reasoning = AnswerReasoning(model_context.chat)

        # Create the state graph
        self.langgraph = StateGraph(OverallState, input=InputState, output=OutputState)
        self._setup_graph()

    def _setup_graph(self):
        self.langgraph.add_node("initial_node_selection", action=self.initial_node_selection)
        self.langgraph.add_node("rational_plan_node", action=self.rational_plan)
        self.langgraph.add_node("atomic_fact_check", self.atomic_fact_check)
        self.langgraph.add_node("chunk_read", self.chunk_read)
        self.langgraph.add_node("neighbor_select", self.neighbor_select)
        self.langgraph.add_node("answer_reasoning", self.answer_reasoning)

        self.langgraph.add_edge(START, "rational_plan_node")
        self.langgraph.add_edge("rational_plan_node", "initial_node_selection")
        self.langgraph.add_edge("initial_node_selection", "atomic_fact_check")

        self.langgraph.add_conditional_edges("atomic_fact_check", self.atomic_fact_condition)
        self.langgraph.add_conditional_edges("chunk_read", self.chunk_condition)
        self.langgraph.add_conditional_edges("neighbor_select", self.neighbor_condition)

        self.langgraph.add_edge("answer_reasoning", END)
        self.langgraph = self.langgraph.compile()

    def invoke(self, question):
        return self.langgraph.invoke({"question": question})

    @staticmethod
    def atomic_fact_condition(state):
        if state.get("chosen_action") == "stop_and_read_neighbor":
            return "neighbor_select"
        elif state.get("chosen_action") == "read_chunk":
            return "chunk_read"

    @staticmethod
    def chunk_condition(state):
        if state.get("chosen_action") == "termination":
            return "answer_reasoning"
        elif state.get("chosen_action") in ["read_subsequent_chunk", "read_previous_chunk", "search_more"]:
            return "chunk_read"
        elif state.get("chosen_action") == "search_neighbor":
            return "neighbor_select"

    @staticmethod
    def neighbor_condition(state):
        if state.get("chosen_action") == "termination":
            return "answer_reasoning"
        elif state.get("chosen_action") == "read_neighbor_node":
            return "atomic_fact_check"