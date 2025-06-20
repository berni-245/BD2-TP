from pymongo import MongoClient
from cassandra.cluster import Cluster
from neo4j import GraphDatabase

"""
# MongoDB
mongo_client = MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client["mi_base"]
mongo_db["productos"].insert_one({"nombre": "Producto A", "precio": 100})
print("✔ Mongo conectado y documento insertado.")

# Cassandra
cluster = Cluster(["127.0.0.1"])
session = cluster.connect()
session.execute("CREATE KEYSPACE IF NOT EXISTS tp WITH replication = {'class':'SimpleStrategy', 'replication_factor':1}")
session.set_keyspace("tp")
session.execute("CREATE TABLE IF NOT EXISTS ordenes (id UUID PRIMARY KEY, producto TEXT, cantidad INT)")
print("✔ Cassandra conectado y tabla lista.")

# Neo4j
neo_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
def crear_nodo(tx):
    tx.run("MERGE (:Proveedor {nombre: 'ProveedorX'})")
with neo_driver.session() as session:
    session.execute_write(crear_nodo)
print("✔ Neo4j conectado y nodo creado.")
"""

print("Main funcionando, código de prueba comentado en el mismo")