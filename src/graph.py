from typing import Set
from pydantic import BaseModel, Field
from graph_utils import graph_to_xml, xml_to_graph


class Node(BaseModel):
    name: str = Field(description="A short and unique identifier for the node.")

    def __hash__(self):
        return hash(self.name.lower())

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.name.lower() == other.name.lower()
        return False


class Edge(BaseModel):
    relationship: str = Field(description="The type of relationship between nodes.")
    source: str = Field(description="The unique identifier of the source node.")
    target: str = Field(description="The unique identifier of the target node.")

    def __hash__(self):
        # Use a tuple of (source, target, relationship) as the hash basis
        return hash((self.source.lower(), self.target.lower(), self.relationship.lower()))

    def __eq__(self, other):
        if isinstance(other, Edge):
            return (
                self.source.lower() == other.source.lower()
                and self.target.lower() == other.target.lower()
                and self.relationship.lower() == other.relationship.lower()
            )
        return False


class Graph(BaseModel):
    nodes: Set[Node] = Field(
        default_factory=set, description="A set of nodes in the graph."
    )
    edges: Set[Edge] = Field(
        default_factory=set, description="A set of edges connecting the nodes."
    )

    def __init__(self, xml_string: str = None, **data):
        super().__init__(**data)
        if xml_string:
            graph = xml_to_graph(xml_string)
            self.nodes = graph.nodes
            self.edges = graph.edges

    def add_node(self, node: Node):
        self.nodes.add(node)

    def add_edge(self, edge: Edge):
        self.edges.add(edge)

    def __str__(self):
        return graph_to_xml(self)
