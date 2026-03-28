from neo4j import GraphDatabase


URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "MeinSicheresPasswort123"
DATABASE = "neo4j"


class Neo4jResetTool:
    def __init__(self, uri, username, password, database):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None):
        with self.driver.session(database=self.database) as session:
            return list(session.run(query, parameters or {}))

    def delete_all_nodes(self):
        print("Deleting all nodes and relationships...")
        query = """
        MATCH (n)
        CALL (n) {
          DETACH DELETE n
        } IN TRANSACTIONS
        """
        self.run_query(query)
        print("All nodes and relationships deleted.")

    def get_constraints(self):
        query = """
        SHOW CONSTRAINTS YIELD name
        RETURN name
        ORDER BY name
        """
        return [record["name"] for record in self.run_query(query)]

    def drop_constraints(self):
        constraints = self.get_constraints()
        if not constraints:
            print("No constraints found.")
            return

        print("Dropping constraints...")
        for name in constraints:
            query = f"DROP CONSTRAINT {name}"
            self.run_query(query)
            print(f"  Dropped constraint: {name}")

    def get_indexes(self):
        query = """
        SHOW INDEXES YIELD name
        RETURN name
        ORDER BY name
        """
        return [record["name"] for record in self.run_query(query)]

    def drop_indexes(self):
        indexes = self.get_indexes()
        if not indexes:
            print("No indexes found.")
            return

        print("Dropping indexes...")
        for name in indexes:
            query = f"DROP INDEX {name}"
            self.run_query(query)
            print(f"  Dropped index: {name}")

    def verify(self):
        node_count_query = "MATCH (n) RETURN count(n) AS count"
        constraint_count_query = "SHOW CONSTRAINTS YIELD name RETURN count(*) AS count"
        index_count_query = "SHOW INDEXES YIELD name RETURN count(*) AS count"

        node_count = self.run_query(node_count_query)[0]["count"]
        constraint_count = self.run_query(constraint_count_query)[0]["count"]
        index_count = self.run_query(index_count_query)[0]["count"]

        print("\nVerification:")
        print(f"  Remaining nodes: {node_count}")
        print(f"  Remaining constraints: {constraint_count}")
        print(f"  Remaining indexes: {index_count}")

    def reset(self):
        self.delete_all_nodes()
        self.drop_constraints()
        self.drop_indexes()
        self.verify()


if __name__ == "__main__":
    tool = Neo4jResetTool(URI, USERNAME, PASSWORD, DATABASE)
    try:
        tool.reset()
    finally:
        tool.close()