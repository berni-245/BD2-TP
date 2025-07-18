import os
from time import sleep

from pymongo import MongoClient
from neo4j import GraphDatabase
from dotenv import load_dotenv
from src.options import Options

def main():
    load_dotenv()

    mongo_client = MongoClient(os.getenv("MONGO_CLIENT_URL"))
    neo_driver = GraphDatabase.driver(
        os.getenv("NEO4J_URL"), # type: ignore
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASS")) # type: ignore
    )

    print("Bienvenido al Backoffice de proveedores de productos en distintas órdenes")
    print("Elija una de las siguientes opciones:")

    options = Options(mongo_client[str(os.getenv("MONGO_DB_NAME"))], neo_driver)

    keep_iterating = True
    while keep_iterating:
        sleep(1)
        print()
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
        print("10 - Visualizar los datos de las órdenes de pedido ordenadas por fecha (incluyendo la razón social del proveedor y el total de la orden sin y con IVA).")
        print("11 - Visualizar todos los productos que aún NO han sido pedidos.")
        print("12 - Visualizar vista que devuelva los datos de los proveedores activos que están inhabilitados.")
        print("13 - Crear nuevos proveedores, eliminar y modificar los ya existentes.")
        print("14 - Crear nuevos productos y modificar los ya existentes.")
        print("15 - Registrar nuevas órdenes de pedido a los proveedores si corresponde.")
        print()
        try:
            option_num = int(input("Ingresar opción (0 - 15): "))
        except ValueError:
            print("Invalid option")
            continue
        print()
        keep_iterating = options.exec_option(option_num)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario.")
        exit(0)
