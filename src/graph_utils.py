from graph import Graph, Node, Edge
from lxml import etree

def xml_to_graph(raw_string: str) -> Graph:
    try:
        # Focus on only the XML segment
        start_tag = "<Graph>"
        end_tag = "</Graph>"
        start_index = raw_string.find(start_tag)
        end_index = raw_string.find(end_tag)
        if start_index == -1 or end_index == -1:
            print("Error: <Graph> or </Graph> tag not found.")
            return ""
        end_index += len(end_tag)
        xml_string = raw_string[start_index:end_index]

        # Parse XML and attempt to recover from malformed XML
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(xml_string, parser=parser)
        graph = Graph()

        # Process Nodes
        for node_elem in root.find("Nodes"):
            if node_elem.tag == "Node" and "name" in node_elem.attrib:
                try:
                    node_name = node_elem.get("name")
                    if node_name:
                        graph.add_node(Node(name=node_name))
                except Exception as e:
                    print(
                        f"Skipping invalid node: {etree.tostring(node_elem)}. Error: {e}"
                    )

        # Process Edges
        for edge_elem in root.find("Edges"):
            if edge_elem.tag == "Edge" and all(
                attr in edge_elem.attrib
                for attr in ["relationship", "source", "target"]
            ):
                try:
                    relationship = edge_elem.get("relationship")
                    source = edge_elem.get("source")
                    target = edge_elem.get("target")
                    graph.add_edge(
                        Edge(relationship=relationship, source=source, target=target)
                    )
                except Exception as e:
                    print(
                        f"Skipping invalid edge: {etree.tostring(edge_elem)}. Error: {e}"
                    )

    except etree.XMLSyntaxError as e:
        print(f"XML Syntax Error: {e}. Skipping malformed chunk.")

    return graph

def graph_to_xml(graph):
        # Create the root element
        root = etree.Element("Graph")

        # Add nodes
        nodes_elem = etree.SubElement(root, "Nodes")
        for node in graph.nodes:
            etree.SubElement(nodes_elem, "Node", name=node.name)

        # Add edges
        edges_elem = etree.SubElement(root, "Edges")
        for edge in graph.edges:
            etree.SubElement(
                edges_elem,
                "Edge",
                relationship=edge.relationship,
                source=edge.source,
                target=edge.target,
            )

        # Convert the ElementTree to a pretty-printed string
        return etree.tostring(root, pretty_print=True, encoding="unicode", method="xml")