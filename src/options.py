from collections import defaultdict
from pymongo.database import Database
from neo4j import Driver
from pprint import pprint
from src.neo4j_utils import new_order
from src.mongo_utils import get_next_sequence
from src.utils import validate_future_date, parse_phone

class Options():
    def __init__(self, mongo_db: Database, neo4j_db: Driver) -> None:
        self.mongo_db = mongo_db
        self.neo4j_db = neo4j_db
        self.options = {
             0: lambda: False,
             1: lambda: option1(self.mongo_db),
             2: lambda: option2(self.mongo_db),
             3: lambda: option3(self.mongo_db),
             4: lambda: option4(self.mongo_db, self.neo4j_db),
             5: lambda: option5(self.mongo_db, self.neo4j_db),
             6: lambda: option6(self.mongo_db, self.neo4j_db),
             7: lambda: option7(self.mongo_db, self.neo4j_db),
            10: lambda: option10(self.mongo_db, self.neo4j_db),
            13: lambda: option13(self.mongo_db, self.neo4j_db),
            14: lambda: option14(self.mongo_db, self.neo4j_db),
            15: lambda: option15(self.mongo_db, self.neo4j_db),
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
                tx.run("MATCH (p:Provider)<-[r]-() RETURN DISTINCT p")
            ]
        )

    mongo_providers = mongo_db["providers"].find({ "id": { "$in": provider_ids } })

    for provider in mongo_providers:
        print(f"CUIT: {provider['CUIT']} - {provider['society_name']}")

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
                    WHERE NOT (p)<-[:OrderedFrom]-()
                    RETURN p
                    """)
            ]
        )

    mongo_providers = mongo_db["providers"].find({ "id": { "$in": provider_ids } })

    for provider in mongo_providers:
        active = "Activo" if provider["active"] else "Inactivo"
        enabled = "Habilitado" if provider["enabled"] else "Deshabilitado"
        print(f"CUIT: {provider['CUIT']} - {provider['society_name']}: {active} - {enabled}")
    return True

def option6(mongo_db: Database, neo_driver: Driver):
    print("----------------------")
    print("Órdenes por proveedor:")
    print("----------------------")

    providers_collection = mongo_db["providers"]

    with neo_driver.session() as session:
        orders_by_provider = session.execute_read(
            lambda tx: [
                record
                for record in tx.run("""
                MATCH (p:Provider)<-[:OrderedFrom]-(o:Order)
                OPTIONAL MATCH (o)-[i:HasItem]->(:Product)
                RETURN p.id AS provider_id,
                    count(DISTINCT o) AS order_count,
                    coalesce(sum(i.price * i.quantity), 0) AS total_cost,
                    coalesce(sum(i.price * i.quantity * (1 + o.iva / 100.0)), 0) AS total_cost_iva
                ORDER BY p.id
                """)
            ]
        )

    provider_ids = [entry["provider_id"] for entry in orders_by_provider]
    mongo_providers = providers_collection.find({ "id": { "$in": provider_ids } })

    provider_info_map = {p["id"]: p for p in mongo_providers}

    for entry in orders_by_provider:
        provider_id = entry["provider_id"]
        mongo_info = provider_info_map.get(provider_id, {})
        print(
            f"CUIT: {mongo_info['CUIT']:>11} - {mongo_info['society_name']}: "
            f"{entry['order_count']} órdenes, "
            f"${entry['total_cost']:.2f} (sin IVA), "
            f"${entry['total_cost_iva']:.2f} (con IVA)"
        )

    return True

def option7(mongo_db: Database, neo_driver: Driver):
    print("-------------------------------------------------------------------------")
    print("Listar todas las órdenes que hayan sido pedidas al proveedor 30660608175:")
    print("-------------------------------------------------------------------------")

    products_collection = mongo_db["products"]
    provider = mongo_db["providers"].find_one({ "CUIT": "30660608175" })
    # provider = mongo_db["providers"].find_one({ "CUIT": "9999" })

    if not provider:
        print("Proveedor con CUIT 30660608175 no encontrado")
        return True

    with neo_driver.session() as session:
        order_details = session.execute_read(
            lambda tx: 
            [
                record for record in
                    tx.run("""
                    MATCH (:Provider {id: $provider_id})<-[:OrderedFrom]-(o:Order)-[i:HasItem]->(p:Product)
                    RETURN o.id as order_id, o.iva as iva,
                        o.expected_delivery_date as date,
                        p.id as product_id, i.quantity as quantity, i.price as price
                    """, provider_id=provider["id"])
            ]
        )

    orders_by_id = defaultdict(lambda: {
        "order_id": None,
        "iva": None,
        "date": None,
        "products": [],
        "total_cost": 0.0,
        "total_cost_iva": 0.0
    })

    for record in order_details:
        id = record["order_id"]
        iva = record["iva"]
        quantity = record["quantity"]
        price = record["price"]
        subtotal = quantity * price
        total_with_iva = subtotal * (1 + iva / 100.0)

        order = orders_by_id[id]
        order["order_id"] = id
        order["iva"] = iva
        order["date"] = record["date"]

        product = products_collection.find_one(
            {"id": record["product_id"]},
            {"_id": 0, "description": 1, "brand": 1}
        )
        order["products"].append({ # type: ignore
            **product, # type: ignore
            "quantity": quantity,
            "price": price
        })
        order["total_cost"] += subtotal
        order["total_cost_iva"] += total_with_iva

    for i, order_id in enumerate(orders_by_id):
        order = orders_by_id[order_id]
        iva = order['iva']

        print(
            f"Orden {i + 1} - Total: "
            f"${order['total_cost']:.2f} sin iva | "
            f"${order['total_cost_iva']:.2f} con iva ({iva}%)"
        )

        for product in order['products']:  # type: ignore
            quantity = product['quantity']
            description = product['description']
            brand = product['brand']
            price = product['price']
            line_total = price * quantity
            line_total_iva = price * quantity * (1 + iva/100) # type: ignore
            print(
                f"    • {quantity} x {description} de {brand} (${price}) "
                f"-> ${line_total:.2f} sin iva | ${line_total_iva:.2f} con iva"
            )

        print()

    return True

def option10(mongo_db: Database, neo_driver: Driver):
    with neo_driver.session() as session:
        results = session.execute_read(
            lambda tx: list(tx.run("""
                MATCH (p:Provider)<-[:OrderedFrom]-(o:Order)
                OPTIONAL MATCH (o)-[i:HasItem]->(:Product)
                ORDER BY o.expected_delivery_date
                RETURN o.id AS order_id,
                       p.id AS provider_id,
                       o.expected_delivery_date AS delivery_date,
                       coalesce(sum(i.price), 0) AS total_cost,
                       coalesce(sum(i.price * (1 + o.iva / 100.0)), 0) AS total_cost_iva
            """))
        )

    for record in results:
        order_id = record["order_id"]
        provider_doc = mongo_db["providers"].find_one({"id": record["provider_id"]})
        if provider_doc:
            provider_society_name = provider_doc["society_name"]
        else:
            continue

        delivery_date = record["delivery_date"]
        total_cost = record["total_cost"]
        total_cost_iva = record["total_cost_iva"]

        print("-----------------------------------")
        print(f"Orden ID: {order_id}")
        print(f"Proveedor Razón social: {provider_society_name}")
        print(f"Fecha de entrega: {delivery_date}")
        print(f"Total sin IVA: ${total_cost:.2f}")
        print(f"Total con IVA: ${total_cost_iva:.2f}")

    return True


def option13(mongo_db: Database, neo_driver: Driver):
    print("-----------------------------------------")
    print("Agregar, modificar o borrar proveedores:")
    print("-----------------------------------------")
    keep_iterating = True
    while keep_iterating:
        print("0 - Regresar")
        print("1 - Agregar un nuevo proveedor.")
        print("2 - Modificar un proveedor existente dado su CUIT.")
        print("3 - Borrar un proveedor existente dado su CUIT.")
        try:
            option = int(input("Elige una opción (0-3): "))
        except ValueError:
            print("Opción inválida")
            continue
        if option > 3:
            print("Opción inválida")
            continue

        if option == 0:
            keep_iterating = False

        if option == 1:
            option13_1(mongo_db, neo_driver)
        if option == 2:
            option13_2(mongo_db)
        if option == 3:
            option13_3(mongo_db, neo_driver)
    return True

def option13_1(mongo_db: Database, neo_driver: Driver):
    print("Ingrese los datos del proveedor a agregar.")
    providers_collection = mongo_db["providers"]

    repetead_key = True
    while repetead_key:
        cuit = input("Ingrese el CUIT no existente de proveedor a insertar: ")
        repetead_key = providers_collection.count_documents({"CUIT": cuit}) > 0
    
    society_name = input("Ingrese la razón social (nombre de sociedad): ")
    society_type = input("Ingrese un tipo de sociedad: ")
    address = input("Ingrese la dirección: ")
    active = input("Ingrese si está activo (y = true / otra respuesta = false): ") == "y"
    enabled = input("Ingrese si está habilitado (y = true / otra respuesta = false): ") == "y"

    phones = []
    more_phones = True
    while more_phones:
        result = parse_phone(input(
            "Para ingresar un número escríbalo en formato '<código de área>;<número>;<tipo de teléfono (F/M)>',\n"
            "cualquier otro formato o dejarlo vacío asumirá que no hay más inserciones: "
        ))
        if result[0]:
            phones.append(result[1])
        else:
            more_phones = False

    id = get_next_sequence(mongo_db, "providers")
    provider_doc = {
        "id": id,
        "CUIT": cuit, # type: ignore
        "society_name": society_name, 
        "society_type": society_type,
        "address": address,
        "active": active,
        "enabled": enabled,
        "phones": phones
    }

    providers_collection.insert_one(provider_doc)
    
    with neo_driver.session() as session:
        session.execute_write(
            lambda tx:
            tx.run("CREATE (:Provider {id: $id})", id=id),
        )


def option13_2(mongo_db: Database):
    print("Para dejar un dato igual, dejar el campo en blanco.")
    providers_collection = mongo_db["providers"]
    original_cuit = input("Ingrese CUIT de proveedor a modificar: ")
    if providers_collection.count_documents({"CUIT": original_cuit}) == 0:
        return
    
    new_doc = {}

    repetead_key = True
    while repetead_key:
        cuit = input("Cambie a un CUIT no existente: ")
        if cuit == "":
            break
        repetead_key = providers_collection.count_documents({"CUIT": cuit}) > 0

    if not cuit == "": # type: ignore
        new_doc["CUIT"] = cuit # type: ignore
    
    society_name = input("Ingrese razón social (nombre de sociedad): ")
    
    if not society_name == "": 
        new_doc["society_name"] = society_name 
    
    society_type = input("Ingrese un tipo de sociedad: ")
    if not society_type == "":
        new_doc["society_type"] = society_type

    address = input("Ingrese la dirección: ")
    if not address == "":
        new_doc["address"] = address

    active = input("Ingrese si está activo (y = true / otra respuesta no vacía = false): ")
    if not active == "":
        new_doc["active"] = active == "y"

    enabled = input("Ingrese si está habilitado (y = true / otra respuesta no vacía = false): ")
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
            
def option13_3(mongo_db: Database, neo_driver: Driver):
    print("Para no borrar, dejar el campo en blanco.")
    providers_collection = mongo_db["providers"]
    original_cuit = input("Ingrese CUIT de proveedor a modificar: ")
    if providers_collection.count_documents({"CUIT": original_cuit}) == 0:
        return
    
    provider = mongo_db["providers"].find_one({"CUIT": original_cuit})
    mongo_db["providers"].delete_one({"CUIT": original_cuit})

    with neo_driver.session() as session:
        session.execute_write(
            lambda tx: tx.run("""
                MATCH (p:Provider {id: $provider_id})-[:Ordered]->(o:Order)
                DETACH DELETE o
                DETACH DELETE p
            """, provider_id=provider['id']), # type: ignore
        )
    
    print("Proveedor eliminado correctamente.")


def option14(mongo_db: Database, neo_driver: Driver):
    print("------------------------------------------------")
    print("Agregar y modificar productos:")
    print("------------------------------------------------")
    keep_iterating = True
    while keep_iterating:
        print("0 - Regresar")
        print("1 - Agregar un nuevo producto.")
        print("2 - Modificar un producto dado su descripción y su categoría.")
        try:
            option = int(input("Elige una opción (0-2): "))
        except ValueError:
            print("Opción inválida")
            continue
        if option > 2:
            print("Opción inválida")
            continue

        if option == 0:
            keep_iterating = False
        if option == 1:
            option14_1(mongo_db, neo_driver)
        if option == 2:
            option14_2(mongo_db)
    return True
    
def option14_1(mongo_db: Database, neo_driver: Driver):
    print("Ingrese los datos del producto a agregar.")
    products_collection = mongo_db["products"]

    repetead_key = True
    while repetead_key:
        print("Ingrese una descripción y marca de producto únicas.")
        description = input("Ingrese la descripción del producto: ")
        brand = input("Ingrese la marca del producto: ")
        repetead_key = products_collection.count_documents({"description": description, "brand": brand}) > 0

    category = input("Ingrese la categoría del producto: ")
    
    valid_input = False
    while not valid_input:
        try:
            price = float(input("Ingrese el precio del producto: "))
            valid_input = True
        except ValueError:
            print("Invalid type, retrying...")
            continue

    valid_input = False
    while not valid_input:
        try:
            current_stock = int(input("Ingresa el stock inicial que poseas: "))
            valid_input = True
        except ValueError:
            print("Invalid type, retrying...")
            continue

    id = get_next_sequence(mongo_db, "products")
    product_doc = {
        "id": id,
        "description": description, # type: ignore
        "brand": brand, # type: ignore
        "category": category,
        "price": price, # type: ignore
        "current_stock": current_stock, # type: ignore
        "future_stock": 0
    }

    products_collection.insert_one(product_doc)
    
    with neo_driver.session() as session:
        session.execute_write(
            lambda tx:
            tx.run("CREATE (:Product {id: $id})", id=id),
        )


def option14_2(mongo_db: Database):
    print("Para dejar un dato igual, dejar el campo en blanco.")
    products_collection = mongo_db["products"]
        
    print("Ingrese una descripción y marca de producto a modificar.")
    original_description = input("Ingrese la descripción del producto: ")
    original_brand = input("Ingrese la marca del producto: ")
    if products_collection.count_documents({"description": original_description, "brand": original_brand}) == 0:
        print("No se encontró el producto con esa descripción y marca.")
        return
    
    new_doc = {}

    repetead_key = True
    while repetead_key:
        print("Ingrese una descripción y marca de producto no existentes.")
        description = input("Ingrese la descripción del producto: ")
        brand = input("Ingrese la marca del producto: ")
        if description == "":
            description = original_description

        if brand == "":
            brand = original_brand

        repetead_key = products_collection.count_documents({"description": description, "brand": brand}) > 0
    
    new_doc["description"] = description # type: ignore
    new_doc["brand"] = brand # type: ignore

    category = input("Ingrese la categoría del producto: ")

    if not category == "":
        new_doc["category"] = category
    
    try:
        price = float(input("Ingrese el precio del producto: "))
        if price >= 0:
            new_doc["price"] = price
    except ValueError:
        print("Invalid type, ignoring...")
        pass

    try:
        current_stock = int(input("Ingrese el nuevo stock actual del producto: "))
        if current_stock >= 0:
            new_doc["current_stock"] = current_stock
    except ValueError:
        print("Invalid type, ignoring...")
        pass    
    
    if new_doc:
        products_collection.update_one(
            {"description": original_description, "brand": original_brand},
            {"$set": new_doc}
        )
        print("Producto actualizado correctamente.")
    else:
        print("No se ingresaron datos para modificar.")    


def option15(mongo_db: Database, neo_driver: Driver):
    print("Ingrese los datos de la orden.")
    providers_collection = mongo_db.providers
    products_collection = mongo_db.products

    while True:
        cuit = input("Ingrese el CUIT de un proveedor existente o deje el campo en blanco para cancelar: ").strip()
        
        if not cuit:
            return True

        provider = providers_collection.find_one({"CUIT": cuit})

        if not provider:
            print("CUIT inválido. Intente nuevamente.")
        elif not provider.get('active', False):
            print("El proveedor no está activo. Intente con otro CUIT.")
        elif not provider.get('enabled', False):
            print("El proveedor no está habilitado. Intente con otro CUIT.")
        else:
            break

    while True:
        date_input = input("Ingresar fecha futura (dd/mm/yyyy): ")
        if not date_input:
            print("Fecha no ingresada. Abortando creación de la orden.")
            return True
        date = validate_future_date(date_input)
        if date:
            break

    while True:
        try:
            iva = float(input("Ingrese el porcentaje de IVA de la orden: "))
            if 0 < iva < 100:
                break
            print("IVA inválido, debe estar en el intervalo (0, 100).")
        except ValueError:
            print("Entrada inválida, debe ingresar un número entero.")
    
    print("Ingrese los datos del producto. Ingresar un campo en blanco finaliza la selección de productos.")
    order_details = []
    while True:
        description = input("Ingrese la descripción del producto: ")
        if not description:
            break
        brand = input("Ingrese la marca del producto: ")
        if not brand:
            break
        product = products_collection.find_one({"description": description, "brand": brand})
        if not product:
            print("El producto especificado no se encuentra en la base. Intente nuevamente.")
        else:
            while True:
                try:
                    quantity = int(input("Ingrese la cantidad requerida: "))
                    if iva > 0:
                        break
                    print("La cantidad debe ser mayor a 0.")
                except ValueError:
                    print("Entrada inválida, debe ingresar un número entero.")
            order_details.append({ 'id': product['id'], 'quantity': quantity, 'price': product['price'] })

    if len(order_details) == 0:
        print("No se ingresaron productos, se cancelará la creación de la orden.")
        return True

    order_id = get_next_sequence(mongo_db, "orders")

    with neo_driver.session() as session:
        session.execute_write(
            new_order,
            provider['id'],
            order_id,
            date_input,
            iva,
            order_details
        )

    return True
