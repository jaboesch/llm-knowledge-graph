from neo4j import AsyncGraphDatabase, GraphDatabase
from graph import Graph
from log_manager import log_error
from typing import List, Dict


def chunked(iterable, batch_size):
    for i in range(0, len(iterable), batch_size):
        yield iterable[i : i + batch_size]


class GraphDatabaseManager:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
        self.sdriver = GraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        await self.driver.close()

    async def reset(self):
        async with self.driver.session() as session:
            await session.run("MATCH ()-[r]->() DELETE r")
            await session.run("MATCH (n) DETACH DELETE n")
            constraints_query = "SHOW CONSTRAINTS"
            constraints = await session.run(constraints_query)
            async for record in constraints:
                constraint_name = record["name"]
                try:
                    await session.run(f"DROP CONSTRAINT {constraint_name}")
                except Exception as e:
                    log_error(f"Error dropping constraint {constraint_name}: {e}")
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:chunk) REQUIRE c.id IS UNIQUE"
            )
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:atomic_fact) REQUIRE c.id IS UNIQUE"
            )
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:key_element) REQUIRE c.id IS UNIQUE"
            )
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (d:document) REQUIRE d.id IS UNIQUE"
            )

    async def import_graph(self, graph: Graph, batch_size=1000):
        await self._import_nodes(graph.nodes, batch_size)
        await self._import_edges(graph.edges, batch_size)

    async def _import_nodes(self, nodes, batch_size):
        async with self.driver.session() as session:
            for batch in chunked(list(nodes), batch_size):
                for node in batch:
                    node_label = node.type  # Extract the type for the node label
                    nodes_data = [
                        {
                            "id": node.id,
                            "content": node.content,
                            "source": getattr(node, "source", None),
                            "index": getattr(node, "index", None),
                            "embeddings": getattr(node, "embeddings", None),
                        }
                    ]
                    query = f"""
                    UNWIND $nodes AS node
                    MERGE (n:{node_label} {{id: node.id}})
                    SET n.content = node.content
                        FOREACH (ignoreMe IN CASE WHEN node.source IS NOT NULL THEN [1] ELSE [] END | SET n.source = node.source)
                        FOREACH (ignoreMe IN CASE WHEN node.index IS NOT NULL THEN [1] ELSE [] END | SET n.index = node.index)
                        FOREACH (ignoreMe IN CASE WHEN node.embeddings IS NOT NULL THEN [1] ELSE [] END | SET n.embeddings = node.embeddings)
                    """
                    try:
                        await session.run(query, nodes=nodes_data)
                    except Exception as e:
                        log_error(f"Error importing nodes batch: {e}")

    async def _import_edges(self, edges, batch_size):
        async with self.driver.session() as session:
            for batch in chunked(list(edges), batch_size):
                for edge in batch:
                    relationship_type = (
                        edge.relationship
                    )  # Extract the relationship type
                    edges_data = [
                        {
                            "source_id": edge.source,
                            "target_id": edge.target,
                        }
                    ]
                    query = f"""
                    UNWIND $edges AS edge
                    MATCH (source {{id: edge.source_id}})
                    MATCH (target {{id: edge.target_id}})
                    MERGE (source)-[r:{relationship_type}]->(target)
                    """
                    try:
                        await session.run(query, edges=edges_data)
                    except Exception as e:
                        log_error(f"Error importing edges batch: {e}")

    async def get_node_by_id(self, node_id: str):
        async with self.driver.session() as session:
            result = await session.run(
                "MATCH (n) WHERE n.id = $id RETURN n", id=node_id
            )
            record = await result.single()
            return record["n"] if record else None
        
    def s_get_node_by_id(self, node_id: str):
        with self.sdriver.session() as session:
            result = session.run(
                "MATCH (n) WHERE n.id = $id RETURN n", id=node_id
            )
            record = result.single()
            return record["n"] if record else None

    def get_atomic_facts(self, key_elements: List[str]) -> List[Dict[str, str]]:
        with self.sdriver.session() as session:
            result = session.run(
                """
                MATCH (k:key_element)<-[:HAS_KEY_ELEMENT]-(fact:atomic_fact)<-[:HAS_ATOMIC_FACT]-(chunk)
                WHERE k.id IN $key_elements
                RETURN DISTINCT chunk.id AS chunk_id, fact.content AS text
                """,
                {"key_elements": key_elements},
            )
            return [
                {"chunk_id": record["chunk_id"], "text": record["text"]}
                for record in result
            ]

    def get_neighbors_by_key_element(self, key_elements) -> List[str]:
        with self.sdriver.session() as session:
            result = session.run(
                """
                MATCH (k:key_element)<-[:HAS_KEY_ELEMENT]-()-[:HAS_KEY_ELEMENT]->(neighbor)
                WHERE k.id IN $key_elements AND NOT neighbor.id IN $key_elements
                WITH neighbor, count(*) AS count
                ORDER BY count DESC LIMIT 50
                RETURN COLLECT(neighbor.id) AS possible_candidates
                """,
                {"key_elements": key_elements},
            )
            record = result.single()
            return record["possible_candidates"] if record else []

    def get_subsequent_chunk_id(self, chunk_id: str) -> str:
        with self.sdriver.session() as session:
            result = session.run(
                """
                MATCH (c:chunk)-[:NEXT]->(next)
                WHERE c.id = $chunk_id
                RETURN next.id AS next
                """,
                {"chunk_id": chunk_id},
            )
            record = result.single()
            return record["next"] if record else None

    def get_previous_chunk_id(self, chunk_id: str) -> str:
        with self.sdriver.session() as session:
            result = session.run(
                """
                MATCH (c:chunk)<-[:NEXT]-(previous)
                WHERE c.id = $chunk_id
                RETURN previous.id AS previous
                """,
                {"chunk_id": chunk_id},
            )
            record = result.single()
            return record["previous"] if record else None

    def get_chunk(self, chunk_id: str) -> Dict[str, str]:
        with self.sdriver.session() as session:
            result = session.run(
                """
                MATCH (c:chunk)
                WHERE c.id = $chunk_id
                RETURN c.id AS chunk_id, c.content AS text
                """,
                {"chunk_id": chunk_id},
            )
            record = result.single()
            return (
                {"chunk_id": record["chunk_id"], "text": record["text"]}
                if record
                else None
            )

    def get_similar_nodes(self, target_embeddings: list, k: int = 50):
        with self.sdriver.session() as session:
            result = session.run(
                """
                WITH $targetEmbeddings AS target_embeddings
                MATCH (n:key_element)
                WHERE n.embeddings IS NOT NULL
                WITH n, gds.similarity.cosine(n.embeddings, target_embeddings) AS similarity
                ORDER BY similarity DESC
                LIMIT $k
                RETURN n.id AS id, similarity
                """,
                {"targetEmbeddings": target_embeddings, "k": k},
            )
            return [{"id": record["id"], "similarity": record["similarity"]} for record in result]

