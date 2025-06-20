from time import sleep
from pymongo import MongoClient
from neo4j import GraphDatabase

from src.mongo_utils import initialize_mongo_db
from src.options import Options

mongo_client = MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client["back_office"]

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

print("Bienvenido al Backoffice de proveedores de productos en distintas órdenes")
print("Elija una de las siguientes opciones:")
sleep(3)

options = Options(mongo_db, 1)

keep_iterating = True
while keep_iterating:
    print("0 - Abandonar aplicación")
    print("1 - Obtener los datos de los proveedores activos y habilitados junto con sus teléfonos.")
    print("2 - Obtener los teléfonos y el código de los proveedores que contengan la palabra 'Tecnología' en su razón social.")
    print("3 - Mostrar cada teléfono junto con los datos del proveedor.")
    print("4 - Obtener todos los proveedores que tengan registrada al menos una orden de pedido.")
    print("5 - Identificar todos los proveedores que NO tengan registrada ninguna orden de pedido.")
    print("6 - Devolver todos los proveedores, con la cantidad de órdenes que tienen registradas y el monto total pedido, con y sin IVA incluido.")
    print("7 - Listar los datos de todas las órdenes que hayan sido pedidas al proveedor cuyo CUIT es 30-66060817-5.")
    print("8 - Mostrar los productos que han sido pedidos al menos una vez.")
    print("9 - Listar los datos de todas las órdenes de pedido que contengan productos de la marca 'COTO'.")
    print("10 - Visualizar vista que devuelva los datos de las órdenes de pedido ordenadas por fecha (incluyendo la razón social del proveedor y el total de la orden sin y con IVA).")
    print("11 - Visualizar vista que devuelva todos los productos que aún NO han sido pedidos.")
    print("12 - Visualizar vista que devuelva los datos de los proveedores activos que están inhabilitados.")
    print("13 - Crear nuevos proveedores, eliminar y modificar los ya existentes.")
    print("14 - Crear nuevos productos y modificar los ya existentes.")
    print("15 - Registrar nuevas órdenes de pedido a los proveedores si corresponde.")
    option_num = int(input("Ingresar opción (0 - 15): "))
    keep_iterating = options.exec_option(option_num)