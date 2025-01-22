from typing import Dict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from graph_reader_agent.state import OverallState
from log_manager import log
from prompt_manager import ANSWER_REASONING_PROMPT, ANSWER_REASONING_ARG_ANALYZE, ANSWER_REASONING_ARG_FINAL_ANSWER

class AnswerReasonOutput(BaseModel):
    analyze: str = Field(description=ANSWER_REASONING_ARG_ANALYZE)
    final_answer: str = Field(description=ANSWER_REASONING_ARG_FINAL_ANSWER)

class AnswerReasoning:
    def __init__(self, chat_model):
        self.chat_model = chat_model

    def __call__(self, state: OverallState) -> OverallState:
        prompt = ChatPromptTemplate.from_messages([
            ("system", ANSWER_REASONING_PROMPT),
            ("human", """
Question: {question}
Notebook: {notebook}"""),
        ])
        chain = prompt | self.chat_model.with_structured_output(AnswerReasonOutput)
        result = chain.invoke({
            "question": state.get("question"),
            "notebook": state.get("notebook"),
        })

        log(f"Final Answer: {result.final_answer}")

        return {
            "answer": result.final_answer,
            "analysis": result.analyze,
            "previous_actions": ["answer_reasoning"],
        }
