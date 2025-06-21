from typing import Any, Dict, Tuple
from pymongo.database import Database, Collection
from neo4j import Driver
from pprint import pprint
from src.mongo_utils import get_next_sequence

class Options():
    def __init__(self, mongo_db: Database, neo4j_db) -> None:
        self.mongo_db = mongo_db
        self.neo4j_db = neo4j_db
        self.options = {
             0: lambda: False,
             1: lambda: option1(self.mongo_db),
             2: lambda: option2(self.mongo_db),
             3: lambda: option3(self.mongo_db),
             4: lambda: option4(self.mongo_db, self.neo4j_db),
             5: lambda: option5(self.mongo_db, self.neo4j_db),
            13: lambda: option13(self.mongo_db)
        }

    def exec_option(self, option_num: int) -> bool:
        if option_num not in self.options:
            print("Opción inválida.")
            return True
        return self.options[option_num]() 

def option1(mongo_db: Database):
    print("----------------------------------------------------")
    print("Proveedores activos y habilitados con sus teléfonos:")
    print("----------------------------------------------------")
    providers = mongo_db["providers"].find({
        "active": True,
        "enabled": True
    })
    for provider in providers:
        pprint({
            "id": provider["id"],
            "society_name": provider["society_name"],
            "phones": provider.get("phones", [])
        })
    return True

def option2(mongo_db: Database):
    print("------------------------------------------------")
    print("Proveedores con 'Tecnología' en la razón social:")
    print("------------------------------------------------")
    providers = mongo_db["providers"].find({
        "society_name": {"$regex": "Tecnología", "$options": "i"}
    })
    for provider in providers:
        pprint({
            "id": provider["id"],
            "society_name": provider["society_name"],
            "phones": provider.get("phones", [])
        })
    return True

def option3(mongo_db: Database):
    print("------------------------------------------------")
    print("Cada teléfono junto con los datos del proveedor:")
    print("------------------------------------------------")
    providers = mongo_db["providers"].find()
    for provider in providers:
        for phone in provider.get("phones", []):
            pprint({
                "provider_id": provider["id"],
                "society_name": provider["society_name"],
                "phone": phone
            })
    return True

def option13(mongo_db: Database):
    print("------------------------------------------------")
    print("Agregar, modificar o borrar proveedores:")
    print("------------------------------------------------")
    keep_iterating = True
    while keep_iterating:
        print("0 - Regresar")
        print("1 - Agregar un nuevo proveedor.")
        print("2 - Modificar un proveedor existente dado su razón social (nombre de sociedad).")
        print("3 - Borrar un proveedor existente dado su razón social (nombre de sociedad).")
        option = int(input("Elige una opción (0-3): "))
        if option > 3:
            print("Opción inválida")
            continue

        if option == 0:
            keep_iterating = False

        if option == 1:
            option13_1(mongo_db)
        if option == 2:
            option13_2(mongo_db)
        if option == 3:
            option13_3(mongo_db)
    return True

def option13_1(mongo_db: Database):
    print("Ingresa los datos del proveedor a agregar.")
    providers_collection = mongo_db["providers"]

    repetead_key = True
    while repetead_key:
        cuit = input("Ingresa el CUIT no existente de proveedor a insertar: ")
        repetead_key = providers_collection.count_documents({"CUIT": cuit}) > 0          
    
    society_name = input("Ingresa la razón social (nombre de sociedad): ")
    society_type = input("Ingresa un tipo de sociedad: ")
    address = input("Ingresa la dirección: ")
    active = input("Ingresa si está activo (y = true / otra respuesta = false): ") == "y"
    enabled = input("Ingresa si está habilitado (y = true / otra respuesta = false): ") == "y"

    phones = []
    more_phones = True
    while more_phones:
        result = parse_phone(input("Para ingresar un número escríbalo en formato '<código de área>;<número>;<tipo de teléfono (F/M)>', cualquier otro formato o dejarlo vacío asumirá que no hay más inserciones: "))
        if result[0]:
            phones.append(result[1])
        else:
            more_phones = False

    provider_doc = {
        "id": get_next_sequence(mongo_db, "providers"),
        "CUIT": cuit, # type: ignore
        "society_name": society_name, 
        "society_type": society_type,
        "address": address,
        "active": active,
        "enabled": enabled,
        "phones": phones
    }

    providers_collection.insert_one(provider_doc)

def option13_2(mongo_db: Database):
    print("Para dejar un dato igual, dejar el campo en blanco.")
    providers_collection = mongo_db["providers"]
    original_cuit = input("Ingresa CUIT de proveedor a modificar: ")
    if providers_collection.count_documents({"CUIT": original_cuit}) == 0:
        return
    
    new_doc = {}

    repetead_key = True
    while repetead_key:
        cuit = input("Cambia a un CUIT no existente: ")
        if cuit == "":
            break
        repetead_key = providers_collection.count_documents({"CUIT": cuit}) > 0

    if not cuit == "": # type: ignore
        new_doc["CUIT"] = cuit # type: ignore
    
    society_name = input("Ingresa razón social (nombre de sociedad): ")
    
    if not society_name == "": 
        new_doc["society_name"] = society_name 
    
    society_type = input("Ingresa un tipo de sociedad: ")
    if not society_type == "":
        new_doc["society_type"] = society_type

    address = input("Ingresa la dirección: ")
    if not address == "":
        new_doc["address"] = address

    active = input("Ingresa si está activo (y = true / otra respuesta no vacía = false): ")
    if not active == "":
        new_doc["active"] = active == "y"

    enabled = input("Ingresa si está habilitado (y = true / otra respuesta no vacía = false): ")
    if not enabled == "":
        new_doc["enabled"] = enabled == "y"

    phone_option = input("1: Replace all phones, 2: Add phones, otherwise skip")
    if phone_option == "1" or phone_option == "2":
        phones = []
        more_phones = True
        while more_phones:
            result = parse_phone(input("Para ingresar un número escríbalo en formato '<código de área>;<número>;<tipo de teléfono (F/M)>', cualquier otro formato o dejarlo vacío asumirá que no hay más inserciones: "))
            if result[0]:
                phones.append(result[1])
            else:
                more_phones = False
        if phone_option == "2":
            new_doc["phones"] = phones
        if phone_option == "1":
            providers_collection.update_one(
                {"CUIT": original_cuit},
                {"$push": {
                    "phones": {
                        "$each": phones
                    }
                }}
            )
    
    if new_doc:
        providers_collection.update_one(
            {"CUIT": original_cuit},
            {"$set": new_doc}
        )
        print("Proveedor actualizado correctamente.")
    else:
        print("No se ingresaron datos para modificar.")    
            
def option13_3(mongo_db: Database):
    print("Para no borrar, dejar el campo en blanco.")
    providers_collection = mongo_db["providers"]
    original_cuit = input("Ingresa CUIT de proveedor a modificar: ")
    if providers_collection.count_documents({"CUIT": original_cuit}) == 0:
        return
    
    mongo_db["providers"].delete_one({"CUIT": original_cuit})
    
    print("Proveedor eliminado correctamente.")
    
    

def parse_phone(raw_str: str) -> Tuple[bool, Dict]:
    split_args = raw_str.split(";")
    if not len(split_args) == 3:
        return (False, {})
    phone = {
        "area_code": split_args[0],
        "phone_number": split_args[1],
        "phone_type": split_args[2]
    }
    return (True, phone)


def option4(mongo_db: Database, neo_driver: Driver):
    print("---------------------------------------------------------------------------------")
    print("Obtener todos los proveedores que tengan registrada al menos una orden de pedido:")
    print("---------------------------------------------------------------------------------")

    with neo_driver.session() as session:
        provider_ids = session.execute_read(
            lambda tx: 
            [
                record["p"]["id"]
                for record in
                tx.run("MATCH (p:Provider)-[r]->() RETURN DISTINCT p")
            ]
        )

    mongo_providers = mongo_db["providers"].find({ "id": { "$in": provider_ids } })

    for provider in mongo_providers:
        print(f"{provider["society_name"]}")

    return True

def option5(mongo_db: Database, neo_driver: Driver):
    print("--------------------------------------------------------------------------")
    print("Obtener todos los proveedores que no tengan registradas ordenes de pedido:")
    print("--------------------------------------------------------------------------")

    with neo_driver.session() as session:
        provider_ids = session.execute_read(
            lambda tx: 
            [
                record["p"]["id"]
                for record in
                    tx.run("""
                    MATCH (p:Provider)
                    WHERE NOT (p)-[:Ordered]->()
                    OPTIONAL MATCH (p)-[r]->()
                    RETURN p, count(r) AS total_relationships
                    """)
            ]
        )

    mongo_providers = mongo_db["providers"].find({ "id": { "$in": provider_ids } })

    for provider in mongo_providers:
        active = "Activo" if provider["active"] else "Inactivo"
        enabled = "Habilitado" if provider["enabled"] else "Deshabilitado"
        print(f"{provider["society_name"]}: {active} - {enabled}")

    return True
