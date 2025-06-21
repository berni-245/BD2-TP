from neo4j import Driver
import pandas as pd
from datetime import datetime

def initialize_neo_db(neo_driver: Driver):
    orders_df = pd.read_csv("data/op.csv", sep=';', encoding='latin1')
    order_details_df = pd.read_csv("data/detalle_op.csv", sep=';', encoding='latin1')
    products_df = pd.read_csv("data/producto.csv", sep=';', encoding='latin1')

    with neo_driver.session() as session:
        for _, order in orders_df.iterrows():
            details = order_details_df[order_details_df['id_pedido'] == order['id_pedido']].to_dict(orient="records") #type:ignore
            product_ids = [d['id_producto'] for d in details]
            matched_products = products_df[products_df['id_producto'].isin(product_ids)]
            total_cost = matched_products['precio'].sum()

            session.execute_write(
                new_order,
                order['id_proveedor'],
                order['id_pedido'],
                order['fecha'],
                details,
                total_cost
            )


def new_order(tx, provider_id, order_id, expected_delivery_date, order_details, total_cost):
    # Ensure Provider and Order nodes exist and connect them
    tx.run(
        """
        MERGE (p:Provider {id: $provider_id})
        CREATE (o:Order {
            id: $order_id,
            expected_delivery_date: date($expected_delivery_date),
            total_cost: $total_cost
        })
        MERGE (p)-[:Ordered]->(o)
        """,
        provider_id=provider_id,
        order_id=order_id,
        expected_delivery_date=datetime.strptime(expected_delivery_date, "%d/%m/%Y").date().isoformat(),
        total_cost=total_cost
    )

    # Add HasItem relationships for each order detail
    for detail in order_details:
        tx.run(
            """
            MATCH (o:Order {id: $order_id})
            MERGE (prod:Product {id: $product_id})
            MERGE (o)-[r:HasItem]->(prod)
            SET r.quantity = $quantity
            """,
            product_id=detail['id_producto'],
            order_id=order_id,
            quantity=detail['cantidad']
        )

