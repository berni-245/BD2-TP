import os

from pymongo import MongoClient
from neo4j import GraphDatabase
from dotenv import load_dotenv
from src.neo4j_utils import initialize_neo_db
from src.mongo_utils import initialize_mongo_db

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGO_CLIENT_URL"))
neo_driver = GraphDatabase.driver(
    str(os.getenv("NEO4J_URL")),
    auth=((os.getenv("NEO4J_USER")), os.getenv("NEO4J_PASS")) # type: ignore
)

initialize_mongo_db(mongo_client[str(os.getenv("MONGO_DB_NAME"))])
initialize_neo_db(neo_driver)
