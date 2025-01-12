import argparse
import asyncio
from config import Config
from logger import Logger
from chat import Chat
from graph_builder import GraphBuilder
from input_manager import InputManager

# TODO refactor to manager names...
# TODO pick and XML format and implement pretty printing for logs
# TODO dig up and implement suggestions for prompt refinement (specify nodes in detail)
# TODO prompt Version: 1.0 -> try "3 part facts"
async def main(args):
    config = Config()
    logger = Logger()
    chat = Chat(config.hf_token)
    input_manager = InputManager()
    graph_builder = GraphBuilder(chat.chat, logger, args.central_topic, args.breadth, chunk_size=1500)
    responses = await graph_builder.build_initial(input_manager.input)
    logger.log(f"Responses {responses}", console=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Knowledge Graph")
    parser.add_argument(
        "central_topic", help="The starting topic for the knowledge graph.", type=str
    )
    parser.add_argument("--breadth", type=int, help="Graph expansion breadth")
    args = parser.parse_args()
    asyncio.run(main(args))
