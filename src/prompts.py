EXTRACTION_PROMPT = """You are an expert in constructing knowledge graphs. Your task is to analyze the provided text, extract all atomic entities as nodes, and identify all meaningful relationships as edges. 

---

**Graph Requirements:**

1. **Nodes:**
   - Extract every atomic entity (e.g., people, places, objects, events, ideas, concepts, dates, organizations, properties, values, etc.) mentioned in the text.
   - For each node, include only the `name` attribute:
     - Format the name in lowercase with underscores.
   - Ensure no duplicate nodes are created.

2. **Edges:**
   - Identify all relationships between the extracted nodes. Each node will likely have multiple relationships. Account for every relationship, no matter how small.
   - Each edge should include:
     - `relationship`: A descriptive label for the relationship (e.g., `friend`, `located_in`, `belongs_to`).
     - `source`: The `name` of the source node.
     - `target`: The `name` of the target node.
   - Ensure every node is connected to at least one other node.

---

**Output:**
Respond in XML format with two sections: `<Nodes>` and `<Edges>`.

**Output Example:**
<Graph>
  <Nodes>
    <Node name="harry_potter"></Node>
    <Node name="hogwarts"></Node>
    <Node name="albus_dumbledore"></Node>
    <Node name="voldemort"></Node>
  </Nodes>
  <Edges>
    <Edge relationship="attends" source="harry_potter" target="hogwarts"></Edge>
    <Edge relationship="leads" source="albus_dumbledore" target="hogwarts"></Edge>
    <Edge relationship="mentor" source="albus_dumbledore" target="harry_potter"></Edge>
    <Edge relationship="enemy_of" source="harry_potter" target="voldemort"></Edge>
  </Edges>
</Graph>

---

### **Step-by-Step Process:**

1. **Extract Nodes:**
   - Exhaustively identify all entities in the input text. Create a `Node` element for each entity with a unique `name`

2. **Generate Edges:**
   - For each node:
     - Evaluate **all possible connections** to all other nodes.
     - Create an `Edge` for each meaningful relationship.
     - Search exhaustively, but never invent relationships, only use facts from the text.
   - Each node should connect to **multiple other nodes** where relevant. The number of edges should significantly exceed the number of nodes.

3. **Ensure Graph Density and Node Existence:**
   - Re-check the graph to ensure it is highly connected:
     - Every node must connect to at least one other node.
     - Nodes should connect to **as many relevant nodes as possible**.
     - If a node appears under-connected, infer additional plausible connections.
  - Re-check the graph to ensure all nodes exist:
     - Every `source` and `target` should be accounted for as a `Node`.
     - If an edge contains an unknown entity, add it to the Nodes list.

4. **Output the Graph in XML Format:**
   - Respond strictly in XML format with properly closed tags.
   - Do not provide any additional commentary.
"""


class Prompt:
    def __init__(self, version, prompt):
        self.version = version
        self.prompt = prompt


class ExtractionPrompt(Prompt):
    def __init__(self):
        super().__init__("1.0", EXTRACTION_PROMPT)
