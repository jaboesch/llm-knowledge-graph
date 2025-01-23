import asyncio
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_text_splitters import TokenTextSplitter
from graph import Graph
from prompt_manager import ExtractionPrompt
from graph_utils import (
    create_chunk_node,
    create_document_node,
    parse_facts_xml,
    create_chunk_edges,
)
from log_manager import log, log_error, log_chat


async def extract_facts_from_chunk(chat, chunk):
    chat_history = [
        SystemMessage(content=ExtractionPrompt.prompt),
        HumanMessage(
            content=f"Input from document chunk #{chunk.index} (may be truncated):\n\n{chunk.content}..."
        ),
    ]
    res = await chat.ainvoke(chat_history)
    chat_history.append(AIMessage(content=res.content))
    log_chat(chat_history)
    nodes, edges = parse_facts_xml(res.content, chunk)
    return nodes, edges


class GraphManager:
    def __init__(self, chat, central_topic, chunk_size=2000):
        self.chat = chat
        self.central_topic = central_topic
        self.chunk_size = chunk_size

    async def build_graph(self, document_content):
        chunk_overlap = self.chunk_size // 10
        log(
            f"Initializing graph build with params: central_topic={self.central_topic}, chunk_size={self.chunk_size}, chunk_overlap={chunk_overlap}, extraction_prompt_version={ExtractionPrompt.version}"
        )

        # Initialize the graph and document node
        graph = Graph()
        document = create_document_node(document_content, "wikipedia")
        graph.add_node(document)

        # Split the document into chunks
        text_splitter = TokenTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=chunk_overlap
        )
        chunks = text_splitter.split_text(document_content)

        # add chunks to graph and run LLM extraction tasks in parallel
        tasks = []
        prev_chunk = None
        for chunk_index, chunk_content in enumerate(chunks):
            chunk = create_chunk_node(chunk_content, chunk_index)
            chunk_edges = create_chunk_edges(document, chunk, prev_chunk)
            prev_chunk = chunk
            graph.add_node(chunk)
            graph.add_edges(chunk_edges)
            tasks.append(extract_facts_from_chunk(self.chat, chunk))
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Add resulting nodes and edges to graph
        for result in results:
            if isinstance(result, Exception):
                log_error(f"Error: {result}")
            else:
                nodes, edges = result
                graph.add_nodes(nodes)
                graph.add_edges(edges)
        log(f"Initial graph build complete.")
        return graph

    @staticmethod
    async def add_entity_embeddings(graph, get_node_by_id, get_embeddings):
        async def get_missing_embeddings(n):
            if n.type == "key_element":
                db_node = await get_node_by_id(n.id)
                if db_node is None:
                    res_embeddings = await get_embeddings(n.content)
                    n.embeddings = res_embeddings
                    log(f"Updated embeddings for node {n.id}: {res_embeddings}")

        await asyncio.gather(*(get_missing_embeddings(n) for n in graph.nodes))
