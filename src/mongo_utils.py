import pandas as pd
from typing import Literal

def collection_exists(mongo_db, name):
    return name in mongo_db.list_collection_names()

def initialize_mongo_db(mongo_db):
    providers_df = pd.read_csv("data/proveedor.csv", sep=';', encoding='latin1')
    telephones_df = pd.read_csv("data/telefono.csv", sep=';', encoding='latin1')
    products_df = pd.read_csv("data/producto.csv", sep=';', encoding='latin1')

    if not collection_exists(mongo_db, "providers"):
        providers_collection = mongo_db["providers"]

        for _, provider in providers_df.iterrows():
            # Filter phones to match the provider id
            telephones = telephones_df[telephones_df["id_proveedor"] == provider["id_proveedor"]]

            phones = []
            for _, tel in telephones.iterrows():
                phones.append({
                    "area_code": tel["codigo_area"],
                    "phone_number": tel["nro_telefono"],
                    "phone_type": tel["tipo"]
                })

            provider_doc = {
                "id": int(provider["id_proveedor"]),
                "CUIT": str(provider["CUIT_proveedor"]),
                "society_name": provider["razon_social"],
                "society_type": provider["tipo_sociedad"],
                "address": provider["direccion"],
                "active": bool(provider["activo"]),
                "enabled": bool(provider["habilitado"]),
                "phones": phones
            }

            providers_collection.insert_one(provider_doc)

    if not collection_exists(mongo_db, "products"):
        products_collection = mongo_db["products"]

        for _, product in products_df.iterrows():
            product_doc = {
                "id": int(product["id_producto"]),
                "description": product["descripcion"],
                "brand": product["marca"],
                "category": product["categoria"],
                "price": product["precio"],
                "current_stock": product["stock_actual"],
                "future_stock": product["stock_futuro"]
            }

            products_collection.insert_one(product_doc)

    mongo_db["counters"].update_one(
        {"_id": "products"},
        {"$set": {"seq": int(products_df["id_producto"].max() + 1)  }},
        upsert=True
    )

    mongo_db["counters"].update_one(
        {"_id": "providers"},
        {"$set": {"seq": int(providers_df["id_proveedor"].max() + 1)}},
        upsert=True
    )

def get_next_sequence(mongo_db, table_name: Literal['providers', 'products']):
    counter = mongo_db["counters"].find_one_and_update(
        {"_id": table_name},
        {"$inc": {"seq": 1}},
        return_document=True,  
        upsert=True 
    )
    return counter["seq"]
