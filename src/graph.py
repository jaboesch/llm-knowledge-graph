from typing import Set, List, Literal, Union
from pydantic import BaseModel, Field


class HashableBaseNode(BaseModel):
    id: str
    type: str
    content: str

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, HashableBaseNode):
            return self.id == other.id
        return False


class DocumentNode(HashableBaseNode):
    type: Literal["document"] = "document"
    id: str = Field(description="MD5 hash of the document content")
    content: str = Field(description="The document content")
    source: str = Field(description="Source URL")


class ChunkNode(HashableBaseNode):
    type: Literal["chunk"] = "chunk"
    id: str = Field(description="MD5 hash of the chunk content")
    content: str = Field(description="The chunk content")
    index: int = Field(description="Index of the chunk")


class AtomicFactNode(HashableBaseNode):
    type: Literal["atomic_fact"] = "atomic_fact"
    id: str = Field(description="MD5 hash of the fact content")
    content: str = Field(description="The atomic fact content")


class KeyElementNode(HashableBaseNode):
    type: Literal["key_element"] = "key_element"
    id: str = Field(description="Normalized content ID")
    content: str = Field(description="The key element content")
    embeddings: list = Field(description="Embeddings of the key element content")


class Edge(BaseModel):
    relationship: Literal["HAS_CHUNK", "NEXT", "HAS_ATOMIC_FACT", "HAS_KEY_ELEMENT"]
    source: str = Field(description="Source Node ID")
    target: str = Field(description="Target Node ID")

    def __hash__(self):
        return hash((self.relationship, self.source, self.target))

    def __eq__(self, other):
        if isinstance(other, Edge):
            return (self.relationship, self.source, self.target) == (
                other.relationship,
                other.source,
                other.target,
            )
        return False


class Graph(BaseModel):
    nodes: Set[Union[DocumentNode, ChunkNode, AtomicFactNode, KeyElementNode]] = Field(
        default_factory=set, description="Set of nodes"
    )
    edges: Set[Edge] = Field(default_factory=set, description="Set of edges")

    def add_node(
        self, node: Union[DocumentNode, ChunkNode, AtomicFactNode, KeyElementNode]
    ):
        if node.id not in {n.id for n in self.nodes}:
            self.nodes.add(node)

    def add_nodes(
        self,
        nodes: List[Union[DocumentNode, ChunkNode, AtomicFactNode, KeyElementNode]],
    ):
        for node in nodes:
            self.add_node(node)

    def add_edge(self, edge: Edge):
        if edge not in self.edges:
            self.edges.add(edge)

    def add_edges(self, edges: List[Edge]):
        for edge in edges:
            self.add_edge(edge)

    def __str__(self):
        """Pretty print the graph data for console or log file."""
        output = ["Graph:"]
        output.append("Nodes:")
        for node in self.nodes:
            output.append(
                f"  - {node.type.capitalize()} Node: {node.id} | Content: {getattr(node, 'content', '')[:50]}..."
            )

        output.append("Edges:")
        for edge in self.edges:
            output.append(
                f"  - {edge.relationship} | Source: {edge.source} -> Target: {edge.target}"
            )

        return "\n".join(output)
