import argparse
import asyncio
from config import Config
from input_manager import InputManager
from model_manager import ModelManager
from graph_manager import GraphManager
from graph_database_manager import GraphDatabaseManager
from graph_reader_agent.graph_reader_agent import GraphReaderAgent
from log_manager import log


async def main(args):
    # initialize modules
    config = Config()
    model_manager = ModelManager(config.hf_token)
    input_manager = InputManager()
    graph_manager = GraphManager(
        model_manager.chat, args.central_topic, args.breadth, chunk_size=1500
    )
    db_manager = GraphDatabaseManager(
        uri=config.neo4j_uri, user=config.neo4j_user, password=config.neo4j_password
    )
    # start with a clean database
    # await db_manager.reset()
    
    graph_reader_agent = GraphReaderAgent(db_manager, model_manager)
    log(graph_reader_agent.invoke("Who is Harry Potter's best friend's sister?"), console=True)
    # build the initial graph
    # graph = await graph_manager.build_initial(input_manager.input)
    # log(graph, console=True)
    # add key entity embeddings and import to neo4j
    # await graph_manager.add_entity_embeddings(graph, db_manager.get_node_by_id, model_manager.embeddings.aembed_query)
    # await db_manager.import_graph(graph)
    # cleanup
    await db_manager.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Knowledge Graph")
    parser.add_argument(
        "central_topic", help="The starting topic for the knowledge graph.", type=str
    )
    parser.add_argument("--breadth", type=int, help="Graph expansion breadth")
    args = parser.parse_args()
    asyncio.run(main(args))
