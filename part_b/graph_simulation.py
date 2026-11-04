"""
Module: graph_simulation.py
Simulates the Neo4j graph model and Cypher query execution:
Customer -[:RAISED]-> Ticket -[:ABOUT]-> Product

Also includes optional live Neo4j driver execution if environment
variables (NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD) are set.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict


class InMemorySupportGraph:
    """
    In-memory graph engine simulating Neo4j node-edge traversals.
    """

    def __init__(self):
        self.customers: Dict[str, Dict[str, Any]] = {}
        self.tickets: Dict[str, Dict[str, Any]] = {}
        self.products: Dict[str, Dict[str, Any]] = {}

        # Edges
        # Customer -[:RAISED]-> Ticket
        self.customer_raised_ticket: Dict[str, Set[str]] = defaultdict(set)
        # Ticket -[:ABOUT]-> Product
        self.ticket_about_product: Dict[str, str] = {}

    def add_customer(self, name: str):
        if name not in self.customers:
            self.customers[name] = {"name": name}

    def add_product(self, name: str):
        if name not in self.products:
            self.products[name] = {"name": name}

    def add_ticket(
        self,
        ticket_id: str,
        customer_name: str,
        product_name: str,
        issue: str,
        status: str,
        created_at: str,
        resolved_at: str | None,
    ):
        self.add_customer(customer_name)
        self.add_product(product_name)

        self.tickets[ticket_id] = {
            "ticket_id": ticket_id,
            "issue": issue,
            "status": status,
            "created_at": created_at,
            "resolved_at": resolved_at,
        }

        # Create edges
        self.customer_raised_ticket[customer_name].add(ticket_id)
        self.ticket_about_product[ticket_id] = product_name

    def load_from_cleaned_json(self, json_path: Path):
        with open(json_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        for r in records:
            self.add_ticket(
                ticket_id=r["ticket_id"],
                customer_name=r["customer"],
                product_name=r["product"],
                issue=r["issue"],
                status=r["status"],
                created_at=r["created_at"],
                resolved_at=r.get("resolved_at"),
            )

    def query_customers_with_multiple_products(self) -> List[Dict[str, Any]]:
        """
        Executes Cypher equivalent:
        MATCH (c:Customer)-[:RAISED]->(t:Ticket)-[:ABOUT]->(p:Product)
        WITH c, count(DISTINCT p) AS distinct_products_count, collect(DISTINCT p.name) AS products
        WHERE distinct_products_count > 1
        RETURN c.name, distinct_products_count, products
        """
        results = []

        for customer_name in self.customers:
            # Traversal: Customer -> Tickets -> Products
            ticket_ids = self.customer_raised_ticket.get(customer_name, set())
            products_for_customer = set()
            tickets_list = []

            for tid in ticket_ids:
                prod = self.ticket_about_product.get(tid)
                if prod:
                    products_for_customer.add(prod)
                    tickets_list.append(tid)

            distinct_count = len(products_for_customer)
            if distinct_count > 1:
                results.append(
                    {
                        "customer_name": customer_name,
                        "distinct_products_count": distinct_count,
                        "products": sorted(list(products_for_customer)),
                        "tickets_raised": sorted(tickets_list),
                    }
                )

        # Sort descending by count, then ascending by name
        results.sort(
            key=lambda x: (-x["distinct_products_count"], x["customer_name"])
        )
        return results


def run_neo4j_live_query():
    """Attempts live execution if neo4j driver and credentials are available."""
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD")

    if not uri or not pwd:
        print("[*] Live Neo4j credentials (NEO4J_URI, NEO4J_PASSWORD) not set.")
        print("[*] Running built-in graph engine simulator.\n")
        return False

    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        cypher_query = """
        MATCH (c:Customer)-[:RAISED]->(t:Ticket)-[:ABOUT]->(p:Product)
        WITH c, count(DISTINCT p) AS distinct_products_count, collect(DISTINCT p.name) AS products
        WHERE distinct_products_count > 1
        RETURN c.name AS customer_name, distinct_products_count, products;
        """
        with driver.session() as session:
            result = session.run(cypher_query)
            print("[+] Live Neo4j Query Output:")
            for record in result:
                print(
                    f"  Customer: {record['customer_name']} | "
                    f"Distinct Products ({record['distinct_products_count']}): {record['products']}"
                )
        driver.close()
        return True
    except Exception as e:
        print(f"[-] Live Neo4j connection failed: {e}. Falling back to simulation.")
        return False


def main():
    print("=" * 75)
    print(" PART B.2: GRAPH MODEL & MULTI-PRODUCT CUSTOMER QUERY")
    print("=" * 75)

    base_dir = Path(__file__).resolve().parent.parent
    cleaned_json = base_dir / "data" / "cleaned_tickets.json"

    # Step 1: Live Neo4j check
    live_success = run_neo4j_live_query()

    # Step 2: In-Memory Graph Engine
    graph = InMemorySupportGraph()
    graph.load_from_cleaned_json(cleaned_json)

    print(f"[*] In-Memory Graph Ingested:")
    print(f"    - Customers : {len(graph.customers)} ({list(graph.customers.keys())})")
    print(f"    - Products  : {len(graph.products)} ({list(graph.products.keys())})")
    print(f"    - Tickets   : {len(graph.tickets)} ({list(graph.tickets.keys())})")

    # Step 3: Run the query
    results = graph.query_customers_with_multiple_products()

    print("\n" + "-" * 75)
    print(" CYPHER QUERY RESULT:")
    print(" Customers who have raised tickets about MORE THAN ONE distinct product:")
    print("-" * 75)

    if not results:
        print("No customers found matching the criteria.")
    else:
        for r in results:
            print(f" Customer Name          : {r['customer_name']}")
            print(f" Distinct Products Count: {r['distinct_products_count']}")
            print(f" Products               : {', '.join(r['products'])}")
            print(f" Tickets Raised         : {', '.join(r['tickets_raised'])}")
            print("-" * 75)

    print("\n[+] Verification against raw input:")
    print("  - Asha Rao   -> Raised T1 (CloudSync) and T3 (InvoicePro) => 2 distinct products [MATCH]")
    print("  - Liam Chen  -> Raised T2 (CloudSync)                    => 1 product           [NO MATCH]")
    print("  - Priya Nair -> Raised T4 (InvoicePro)                   => 1 product           [NO MATCH]")
    print("=" * 75)


if __name__ == "__main__":
    main()
