from pymongo import MongoClient
from neo4j import GraphDatabase

from src.mongo_utils import initialize_mongo_db

mongo_client = MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client["Backoffice"]

initialize_mongo_db(mongo_db)

"""
# Neo4j
neo_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
def crear_nodo(tx):
    tx.run("MERGE (:Proveedor {nombre: 'ProveedorX'})")
with neo_driver.session() as session:
    session.execute_write(crear_nodo)
print("✔ Neo4j conectado y nodo creado.")

print("Main funcionando, código de prueba comentado en el mismo")
"""