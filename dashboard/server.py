"""
Zero-dependency local HTTP server and REST API for the Customer Support Tickets Dashboard.
Serves static frontend and provides JSON endpoints for Part A, Part B.1, and Part B.2.
"""

from __future__ import annotations
import http.server
import json
import socketserver
import sys
from pathlib import Path
from typing import Any, Dict

# Resolve project root
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "part_a"))
sys.path.insert(0, str(ROOT_DIR / "part_b"))

from part_a.data_cleaner import TicketDataCleaner
from part_a.analytics import TicketAnalytics
from part_b.evaluate_summaries import evaluate_all, compute_token_metrics
from part_b.graph_simulation import InMemorySupportGraph

PORT = 8000
STATIC_DIR = Path(__file__).resolve().parent / "static"


def get_dashboard_data() -> Dict[str, Any]:
    raw_path = ROOT_DIR / "data" / "raw_tickets.json"
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_tickets = json.load(f)

    cleaner = TicketDataCleaner()
    cleaned_records = cleaner.clean_records(raw_tickets)
    cleaned_dicts = [r.to_dict() for r in cleaned_records]

    # Analytics
    product_status_counts = TicketAnalytics.compute_status_counts_per_product(cleaned_records)
    resolution_times = TicketAnalytics.compute_resolution_times(cleaned_records)

    # LLM Evaluations
    evals = [
        {
            "ticket_id": "T1",
            "product": "CloudSync",
            "reference": "Customer locked out of CloudSync after resetting their password.",
            "llm": "User cannot log in to CloudSync.",
            "scores": {
                "accuracy": 5.0,
                "completeness": 3.0,
                "entity": 5.0,
                "utility": 4.0,
            },
            "composite": 4.15,
            "grade": "B+ (83%)",
            "justification": "Accurate, but omitted the critical causal trigger ('after resetting their password').",
            "token_metrics": compute_token_metrics(
                "Customer locked out of CloudSync after resetting their password.",
                "User cannot log in to CloudSync.",
            ),
        },
        {
            "ticket_id": "T2",
            "product": "CloudSync",
            "reference": "CloudSync sync process hangs near completion.",
            "llm": "Sync is stuck.",
            "scores": {
                "accuracy": 5.0,
                "completeness": 1.5,
                "entity": 1.0,
                "utility": 2.0,
            },
            "composite": 2.53,
            "grade": "F (51%)",
            "justification": "Severe loss of context. Omitted product entity ('CloudSync') and completion stage ('90%' / 'near completion').",
            "token_metrics": compute_token_metrics(
                "CloudSync sync process hangs near completion.",
                "Sync is stuck.",
            ),
        },
        {
            "ticket_id": "T3",
            "product": "InvoicePro",
            "reference": "InvoicePro-generated PDFs are missing invoice line items.",
            "llm": "PDF export has a missing items bug in InvoicePro.",
            "scores": {
                "accuracy": 4.8,
                "completeness": 4.5,
                "entity": 5.0,
                "utility": 4.8,
            },
            "composite": 4.74,
            "grade": "A (95%)",
            "justification": "Preserved product, subsystem, and symptom. High triage value.",
            "token_metrics": compute_token_metrics(
                "InvoicePro-generated PDFs are missing invoice line items.",
                "PDF export has a missing items bug in InvoicePro.",
            ),
        },
    ]

    # Graph Data for Vis.js
    graph = InMemorySupportGraph()
    clean_path = ROOT_DIR / "data" / "cleaned_tickets.json"
    graph.load_from_cleaned_json(clean_path)
    multi_product_customers = graph.query_customers_with_multiple_products()

    # Build vis.js nodes & edges
    nodes = []
    edges = []

    # Customers (Blue)
    for c_name in graph.customers:
        is_highlighted = any(m["customer_name"] == c_name for m in multi_product_customers)
        nodes.append({
            "id": f"cust_{c_name}",
            "label": c_name,
            "group": "Customer",
            "color": "#3B82F6" if not is_highlighted else "#8B5CF6",
            "shape": "ellipse",
            "font": {"color": "#ffffff", "face": "Inter"},
            "title": f"Customer: {c_name}" + (" (Multi-product!)" if is_highlighted else ""),
        })

    # Tickets (Orange)
    for tid, tinfo in graph.tickets:
        pass
    for tid, tinfo in graph.tickets.items():
        nodes.append({
            "id": f"ticket_{tid}",
            "label": f"Ticket {tid}\n({tinfo['status']})",
            "group": "Ticket",
            "color": "#F59E0B" if tinfo['status'] == 'open' else "#10B981",
            "shape": "box",
            "font": {"color": "#ffffff", "face": "Inter"},
            "title": f"Ticket: {tid}<br>Issue: {tinfo['issue']}<br>Status: {tinfo['status']}",
        })

    # Products (Emerald Green)
    for p_name in graph.products:
        nodes.append({
            "id": f"prod_{p_name}",
            "label": f"📦 {p_name}",
            "group": "Product",
            "color": "#059669",
            "shape": "database",
            "font": {"color": "#ffffff", "face": "Inter"},
            "title": f"Product: {p_name}",
        })

    # Edges: Customer -RAISED-> Ticket
    for c_name, ticket_ids in graph.customer_raised_ticket.items():
        for tid in ticket_ids:
            edges.append({
                "from": f"cust_{c_name}",
                "to": f"ticket_{tid}",
                "label": "RAISED",
                "arrows": "to",
                "color": {"color": "#94A3B8"},
            })

    # Edges: Ticket -ABOUT-> Product
    for tid, p_name in graph.ticket_about_product.items():
        edges.append({
            "from": f"ticket_{tid}",
            "to": f"prod_{p_name}",
            "label": "ABOUT",
            "arrows": "to",
            "color": {"color": "#94A3B8"},
        })

    return {
        "raw_tickets": raw_tickets,
        "cleaned_tickets": cleaned_dicts,
        "cleaning_stats": cleaner.cleaning_stats,
        "product_status_counts": product_status_counts,
        "resolution_times": resolution_times,
        "evaluations": evals,
        "graph": {
            "nodes": nodes,
            "edges": edges,
            "multi_product_customers": multi_product_customers,
        },
    }


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self):
        if self.path == "/api/data":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            data = get_dashboard_data()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return
        elif self.path in ("/", "/index.html"):
            self.path = "/index.html"
            return super().do_GET()
        else:
            return super().do_GET()


def run_server(port=PORT):
    # Ensure static directory exists
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    server_address = ("", port)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(server_address, DashboardHandler) as httpd:
        print("=" * 70)
        print(f"[+] Customer Support Tickets Web Dashboard running at:")
        print(f"    http://localhost:{port}")
        print("    Press Ctrl+C to stop the server.")
        print("=" * 70)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down dashboard server...")
            httpd.server_close()



if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(p)
