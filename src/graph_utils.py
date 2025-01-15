from typing import Union, List
from lxml import etree
from graph import Edge, AtomicFactNode, KeyElementNode, DocumentNode, ChunkNode
from log_manager import log_error
import hashlib


def md5(content: str) -> str:
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def normalize(content: str) -> str:
    return " ".join(content.lower().strip().split())


def create_document_node(content: str, source: str) -> DocumentNode:
    return DocumentNode(
        id=md5(content),
        content=content,
        source=source,
    )


def create_chunk_node(content: str, index: int) -> ChunkNode:
    return ChunkNode(
        id=md5(content),
        content=content,
        index=index,
    )


def create_chunk_edges(
    document: DocumentNode, chunk: ChunkNode, prev_chunk: Union[ChunkNode, None]
) -> List[Edge]:
    edges = [Edge(relationship="HAS_CHUNK", source=document.id, target=chunk.id)]
    if prev_chunk:
        edges.append(Edge(relationship="NEXT", source=prev_chunk.id, target=chunk.id))
    return edges


def parse_facts_xml(raw_string: str, chunk: ChunkNode):
    # Focus on only the XML segment
    start_tag = "<Facts>"
    end_tag = "</Facts>"
    start_index = raw_string.find(start_tag)
    end_index = raw_string.find(end_tag)
    if start_index == -1:
        log_error("Error: leading <Facts> or </Facts> tag not found.")
        return ""
    if end_index == -1:
        log_error("Error: ending </Facts> tag not found. Attempting recovery.")
        raw_string += "</Facts>"
        end_index = len(raw_string)
    else:
        end_index += len(end_tag)
    xml_string = raw_string[start_index:end_index]

    nodes = []
    edges = []

    try:
        # Parse the facts XML
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(xml_string, parser=parser)
        for atomic_fact_elem in root.findall("AtomicFact"):
            fact_content = atomic_fact_elem.get("fact")
            if not fact_content:
                continue

            # Add atomic fact node
            atomic_fact_node = AtomicFactNode(
                id=md5(fact_content), content=fact_content
            )
            nodes.append(atomic_fact_node)
            edges.append(
                Edge(
                    relationship="HAS_ATOMIC_FACT",
                    source=chunk.id,
                    target=atomic_fact_node.id,
                )
            )

            for key_element_elem in atomic_fact_elem.findall("KeyElement"):
                element_content = key_element_elem.get("element")
                if not element_content:
                    continue

                # Add key element node
                key_element_node = KeyElementNode(
                    id=normalize(element_content),
                    content=element_content,
                    embeddings=[],
                )
                nodes.append(key_element_node)

                # Add an edge from atomic fact to key element
                edges.append(
                    Edge(
                        relationship="HAS_KEY_ELEMENT",
                        source=atomic_fact_node.id,
                        target=key_element_node.id,
                    )
                )

        return nodes, edges
    except etree.XMLSyntaxError as e:
        log_error(f"XML Syntax Error: {e}. Skipping malformed chunk.")
        raise ValueError(f"Invalid XML: {e}")

