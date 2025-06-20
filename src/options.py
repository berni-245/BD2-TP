from pymongo.database import Database
from pprint import pprint

class Options():
    def __init__(self, mongo_db: Database, neo4j_db) -> None:
        self.mongo_db = mongo_db
        self.neo4j_db = neo4j_db
        self.options = {
            0: lambda: False,
            1: lambda: option1(self.mongo_db),
            2: lambda: option2(self.mongo_db),
            3: lambda: option3(self.mongo_db),
        }

    def exec_option(self, option_num: int) -> bool:
        if option_num not in self.options:
            print("Opción inválida.")
            return True
        return self.options[option_num]() 

def option1(mongo_db: Database):
    print("------------------------------------------------")
    print("Proveedores activos y habilitados con sus teléfonos:")
    print("------------------------------------------------")
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

    
