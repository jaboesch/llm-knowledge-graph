import asyncio
from datetime import datetime
from prompts import ExtractionPrompt
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_text_splitters import TokenTextSplitter


async def ainvoke(chat, chat_history):
    res = await chat.ainvoke(chat_history)
    chat_history.append(AIMessage(content=res.content))
    return res.content, chat_history


def print_chat_history(chat_history):
    for message in chat_history:
        message.pretty_print()


class GraphBuilder:
    def __init__(self, chat, logger, central_topic, breadth, chunk_size=2000):
        self.chat = chat
        self.central_topic = central_topic
        self.breadth = breadth
        self.chunk_size = chunk_size
        self.logger = logger

    async def build_initial(self, text):
        extraction_prompt = ExtractionPrompt()
        chunk_overlap = self.chunk_size // 10
        self.logger.log(
            f"Initializing graph build with params: central_topic={self.central_topic}, breadth={self.breadth}, chunk_size={self.chunk_size}, chunk_overlap={chunk_overlap}, extraction_prompt_version={extraction_prompt.version}"
        )
        text_splitter = TokenTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=chunk_overlap
        )
        chunks = text_splitter.split_text(text)
        # define tasks
        tasks = []
        for index, chunk in enumerate(chunks):
            chunk_id = index + 1
            chat_history = [
                SystemMessage(content=extraction_prompt.prompt),
                HumanMessage(
                    content=f"Input from document chunk #{chunk_id} (may be truncated):\n\n{chunk}..."
                ),
            ]
            tasks.append(ainvoke(self.chat, chat_history))
        # run in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.log_error(f"Error: {result}")
            else:
                res_content, chat_history = result
                responses.append(res_content)
                self.logger.log(f"Chat Completion:\n{chat_history}")
        self.logger.log(
            f"Initial graph build complete with {len(responses)} responses."
        )
        return responses
