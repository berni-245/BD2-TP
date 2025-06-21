from neo4j import Driver
import pandas as pd
from datetime import datetime

def initialize_neo_db(neo_driver: Driver):
    orders_df = pd.read_csv("data/op.csv", sep=';', encoding='latin1')
    order_details_df = pd.read_csv("data/detalle_op.csv", sep=';', encoding='latin1')
    products_df = pd.read_csv("data/producto.csv", sep=';', encoding='latin1')
    price_lookup = dict(zip(products_df['id_producto'], products_df['precio']))

    with neo_driver.session() as session:
        for _, order in orders_df.iterrows():
            details = order_details_df[order_details_df['id_pedido'] == order['id_pedido']].to_dict(orient="records") #type:ignore
            mapped_details = [
                {
                    'id': detail['id_producto'],
                    'quantity': detail['cantidad'],
                    'price': price_lookup.get(detail['id_producto'], 0)
                }
                for detail in details
            ]

            session.execute_write(
                new_order,
                order['id_proveedor'],
                order['id_pedido'],
                order['fecha'],
                order['iva'],
                mapped_details,
            )


def new_order(tx, provider_id, order_id, expected_delivery_date, iva, order_details):
    tx.run(
        """
        MERGE (p:Provider {id: $provider_id})
        CREATE (o:Order {
            id: $order_id,
            expected_delivery_date: date($expected_delivery_date),
            iva: $iva
        })
        MERGE (o)-[:OrderedFrom]->(p)
        """,
        provider_id=provider_id,
        order_id=order_id,
        expected_delivery_date=datetime.strptime(expected_delivery_date, "%d/%m/%Y").date().isoformat(),
        iva=iva,
    )

    for detail in order_details:
        tx.run(
            """
            MATCH (o:Order {id: $order_id})
            MERGE (prod:Product {id: $product_id})
            MERGE (o)-[r:HasItem {price: $price}]->(prod)
            SET r.quantity = $quantity
            """,
            product_id=detail['id'],
            order_id=order_id,
            price=detail['price'],
            quantity=detail['quantity'],
        )

