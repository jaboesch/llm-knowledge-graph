import os
from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()
        self.neo4j_uri = os.environ.get("NEO4J_URI", "MISSING FROM .env FILE")
        self.neo4j_user = os.environ.get("NEO4J_USERNAME", "MISSING FROM .env FILE")
        self.neo4j_password = os.environ.get("NEO4J_PASSWORD", "MISSING FROM .env FILE")
        self.neo4j_database = os.environ.get("NEO4J_DATABASE", "neo4j")
        self.hf_token = os.environ.get("HF_API_KEY", "MISSING FROM .env FILE")
