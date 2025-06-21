import pandas as pd
from pymongo import ReturnDocument
from pymongo.database import Database
from typing import Literal

def collection_exists(mongo_db: Database, name: str):
    return name in mongo_db.list_collection_names()

def initialize_mongo_db(mongo_db: Database):
    providers_df = pd.read_csv("data/proveedor.csv", sep=';', encoding='latin1')
    telephones_df = pd.read_csv("data/telefono.csv", sep=';', encoding='latin1')
    products_df = pd.read_csv("data/producto.csv", sep=';', encoding='latin1')
    orders_df = pd.read_csv("data/op.csv", sep=';', encoding='latin1')

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

            providers_collection.create_index(
                [("CUIT", 1)],
                unique=True,
                name="unique_CUIT"
            )

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

            products_collection.create_index(
                [("brand", 1), ("description", 1)],
                unique=True,
                name="unique_brand_description"
            )

    if not collection_exists(mongo_db, "counters"):
        mongo_db["counters"].update_one(
            {"_id": "products"},
            {"$set": {"seq": int(products_df["id_producto"].max() + 1) }},
            upsert=True
        )

        mongo_db["counters"].update_one(
            {"_id": "providers"},
            {"$set": {"seq": int(providers_df["id_proveedor"].max() + 1)}},
            upsert=True
        )

        mongo_db["counters"].update_one(
            {"_id": "orders"},
            {"$set": {"seq": int(orders_df["id_pedido"].max() + 1)}},
            upsert=True
        )

def get_next_sequence(mongo_db: Database, table_name: Literal['providers', 'products', 'orders']):
    counter = mongo_db["counters"].find_one_and_update(
        {"_id": table_name},
        {"$inc": {"seq": 1}},
        return_document=ReturnDocument.BEFORE,  # increment after getting what to return
        upsert=True 
    )
    return counter["seq"]
