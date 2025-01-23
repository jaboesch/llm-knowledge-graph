import argparse
import asyncio
from config import Config
from input_manager import InputManager
from model_manager import ModelManager
from graph_manager import GraphManager
from graph_database_manager import GraphDatabaseManager
from graph_reader_agent.graph_reader_agent import GraphReaderAgent
from log_manager import log


async def build_graph(topic):
    config = Config()
    model_manager = ModelManager(config.hf_token)
    input_manager = InputManager(topic)
    graph_manager = GraphManager(
        model_manager.chat, topic, chunk_size=1500
    )
    db_manager = GraphDatabaseManager(
        uri=config.neo4j_uri, user=config.neo4j_user, password=config.neo4j_password, database=config.neo4j_database
    )
    graph = await graph_manager.build_graph(input_manager.input)
    await graph_manager.add_entity_embeddings(graph, db_manager.get_node_by_id, model_manager.embeddings.aembed_query)
    await db_manager.import_graph(graph)
    await db_manager.close()

    
async def read_graph(question):
    config = Config()
    model_manager = ModelManager(config.hf_token, chat_model="gpt-4o")
    db_manager = GraphDatabaseManager(
        uri=config.neo4j_uri, user=config.neo4j_user, password=config.neo4j_password, database=config.neo4j_database
    )
    graph_reader_agent = GraphReaderAgent(db_manager, model_manager)
    log(graph_reader_agent.invoke(question), console=True)
    

async def expand_graph(breadth):
    # TODO: Implement graph expansion logic to query the `breadth` most important graph nodes (possibly via neighbor/edge count), 
    # research those nodes (via wikipedia for now), and add the knowledge using `build_graph()`.
    raise NotImplementedError("Graph expansion is not yet implemented.")


async def reset_graph():
    config = Config()
    db_manager = GraphDatabaseManager(
        uri=config.neo4j_uri, user=config.neo4j_user, password=config.neo4j_password, database=config.neo4j_database
    )
    await db_manager.reset()
    await db_manager.close()


def main(args):
    if args.command == "read":
        asyncio.run(read_graph(args.input))
    elif args.command == "build":
        asyncio.run(build_graph(args.input))
    elif args.command == "expand":
        asyncio.run(expand_graph(args.breadth))
    elif args.command == "reset":
        asyncio.run(reset_graph())
    else:
        raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Knowledge Graph")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands")

    # Subcommand: build
    build_parser = subparsers.add_parser("build", help="Build a new knowledge graph.")
    build_parser.add_argument("input", type=str, help="The topic to build the graph around.")
    
    # Subcommand: read
    read_parser = subparsers.add_parser("read", help="Read from the knowledge graph.")
    read_parser.add_argument("input", type=str, help="The question to query the graph.")
    
    # Subcommand: reset
    reset_parser = subparsers.add_parser("reset", help="Reset the knowledge graph.")

    # Subcommand: expand
    expand_parser = subparsers.add_parser("expand", help="Expand the existing knowledge graph.")
    expand_parser.add_argument("breadth", type=int, help="Number of nodes to expand.")

    args = parser.parse_args()
    main(args)

# Sample questions for read command:
# "What is the middle name of the person who kills the parents of the protagonist of the wizard novel series by J.K. Rowling?"
# "A popular novel was compared by the Sunday Times to works by Roald Dahls. How many copies of this novel have been sold?"