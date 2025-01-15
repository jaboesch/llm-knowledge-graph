import asyncio
from neo4j import AsyncGraphDatabase
from graph import Graph, DocumentNode, ChunkNode, KeyElementNode
from log_manager import log_error


def chunked(iterable, batch_size):
    for i in range(0, len(iterable), batch_size):
        yield iterable[i : i + batch_size]


class GraphDatabaseManager:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

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
