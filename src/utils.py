from collections import defaultdict
from datetime import datetime
from typing import Dict, Tuple

from pymongo.database import Database

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

def validate_future_date(date):
    try:
        date_obj = datetime.strptime(date, "%d/%m/%Y").date()
        today = datetime.today().date()

        if date_obj <= today:
            print("La fecha debe ser en el futuro.")
            return None
        else:
            return date_obj

    except ValueError:
        print("Formato inválido.")
        return None


def parse_option_details(mongo_db: Database, order_details):
    products_collection = mongo_db["products"]
    providers_collection = mongo_db["providers"]

    orders_by_provider = defaultdict(lambda: {
        "provider": None,
        "orders": defaultdict(lambda: {
            "order_id": None,
            "iva": None,
            "date": None,
            "products": [],
            "total_cost": 0.0,
            "total_cost_iva": 0.0
        })
    })

    for record in order_details:
        provider_id = record["provider_id"]
        order_id = record["order_id"]
        iva = record["iva"]
        quantity = record["quantity"]
        price = record["price"]
        subtotal = quantity * price
        total_with_iva = subtotal * (1 + iva / 100.0)

        # Get the provider entry
        provider_entry = orders_by_provider[provider_id]

        # Only fetch and assign the provider once
        if provider_entry["provider"] is None:
            provider_entry["provider"] = providers_collection.find_one({"id": provider_id})

        # Access the order dictionary
        order = provider_entry["orders"][order_id] #type: ignore
        order["order_id"] = order_id
        order["iva"] = iva
        order["date"] = record["date"]

        product = products_collection.find_one(
            {"id": record["product_id"]},
            {"_id": 0, "description": 1, "brand": 1}
        )

        order["products"].append({ #type: ignore
            **product, #type: ignore
            "quantity": quantity,
            "price": price
        })
        order["total_cost"] += subtotal
        order["total_cost_iva"] += total_with_iva

    return orders_by_provider

def print_order_details(orders_by_provider):
    for _, provider_data in orders_by_provider.items():
        provider = provider_data["provider"]
        provider_name = provider["society_name"]
        cuit = provider["CUIT"]

        print("-----------------------------------------------")
        print(f"Proveedor {provider_name} (CUIT: {cuit:>11})")
        print("-----------------------------------------------")

        for i, (_, order) in enumerate(provider_data["orders"].items(), start=1):
            iva = order['iva']
            print(
                f"  Orden {i} - Total: "
                f"${order['total_cost']:.2f} sin IVA | "
                f"${order['total_cost_iva']:.2f} con IVA ({iva}%)"
            )

            for product in order['products']:
                quantity = product['quantity']
                description = product['description']
                brand = product['brand']
                price = product['price']
                line_total = price * quantity
                line_total_iva = line_total * (1 + iva / 100.0)

                print(
                    f"    • {quantity} x {description} de {brand} (${price}) "
                    f"-> ${line_total:.2f} sin IVA | ${line_total_iva:.2f} con IVA"
                )

            print()
