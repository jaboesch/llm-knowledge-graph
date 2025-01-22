from pydantic import BaseModel
from graph_reader_agent.state import OverallState
from langchain_core.prompts import ChatPromptTemplate
from prompt_manager import RATIONAL_PLAN_PROMPT
from log_manager import log

class RationalPlanOutput(BaseModel):
    rational_plan: str

class RationalPlan:
    def __init__(self, chat_model):
        self.chat_model = chat_model

    def __call__(self, state: OverallState) -> OverallState:
        prompt = ChatPromptTemplate.from_messages([
            ("system", RATIONAL_PLAN_PROMPT),
            ("human", "{question}"),
        ])
        chain = prompt | self.chat_model.with_structured_output(RationalPlanOutput)
        result = chain.invoke({"question": state.get("question")})
        log(f"Rational Plan: {result.rational_plan}")
        return {
            "rational_plan": result.rational_plan,
            "previous_actions": ["rational_plan"],
        }