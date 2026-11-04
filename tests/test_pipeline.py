"""
Unit Tests for Customer Support Tickets Pipeline (Part A & Part B).
Uses Python standard library unittest.
"""

import unittest
from datetime import datetime
import sys
from pathlib import Path

# Add project root to sys.path
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "part_a"))
sys.path.insert(0, str(base_dir / "part_b"))

from part_a.data_cleaner import TicketDataCleaner, TicketRecord
from part_a.analytics import TicketAnalytics
from part_b.graph_simulation import InMemorySupportGraph


class TestTicketDataCleaner(unittest.TestCase):
    def setUp(self):
        self.raw_data = [
            {
                "ticket_id": "T1",
                "customer": "Asha Rao",
                "product": "CloudSync",
                "issue": "Login fails after password reset",
                "status": "resolved",
                "created_at": "2026-09-01T09:00:00",
                "resolved_at": "2026-09-01T14:00:00",
            },
            {
                "ticket_id": "T2",
                "customer": "Liam Chen",
                "product": "CloudSync",
                "issue": "Sync stuck at 90%",
                "status": "open",
                "created_at": "2026-09-02T10:00:00",
                "resolved_at": None,
            },
            {
                "ticket_id": "T3",
                "customer": "Asha Rao",
                "product": "InvoicePro",
                "issue": "PDF export missing line items",
                "status": "resolved",
                "created_at": "2026-09-03T11:00:00",
                "resolved_at": "2026-09-04T09:00:00",
            },
            {
                "ticket_id": "T1",
                "customer": "Asha Rao",
                "product": "CloudSync",
                "issue": "Login fails after password reset",
                "status": "resolved",
                "created_at": "2026-09-01T09:00:00",
                "resolved_at": "2026-09-01T14:00:00",
            },
            {
                "ticket_id": "T4",
                "customer": "Priya Nair",
                "product": "InvoicePro",
                "issue": "",
                "status": "open",
                "created_at": "2026-09-05T08:30:00",
                "resolved_at": None,
            },
        ]
        self.cleaner = TicketDataCleaner()

    def test_deduplication(self):
        cleaned = self.cleaner.clean_records(self.raw_data)
        # Raw count 5, exactly 1 duplicate of T1 -> 4 cleaned records
        self.assertEqual(len(cleaned), 4)
        ticket_ids = [r.ticket_id for r in cleaned]
        self.assertEqual(ticket_ids, ["T1", "T2", "T3", "T4"])
        self.assertEqual(self.cleaner.cleaning_stats["exact_duplicates_removed"], 1)

    def test_missing_issue_handling(self):
        cleaned = self.cleaner.clean_records(self.raw_data)
        t4 = next(r for r in cleaned if r.ticket_id == "T4")
        self.assertEqual(t4.issue, TicketDataCleaner.DEFAULT_ISSUE_PLACEHOLDER)
        self.assertEqual(self.cleaner.cleaning_stats["missing_issues_handled"], 1)

    def test_status_counts_per_product(self):
        cleaned = self.cleaner.clean_records(self.raw_data)
        counts = TicketAnalytics.compute_status_counts_per_product(cleaned)

        self.assertIn("CloudSync", counts)
        self.assertIn("InvoicePro", counts)

        self.assertEqual(counts["CloudSync"]["open"], 1)
        self.assertEqual(counts["CloudSync"]["resolved"], 1)
        self.assertEqual(counts["CloudSync"]["total"], 2)

        self.assertEqual(counts["InvoicePro"]["open"], 1)
        self.assertEqual(counts["InvoicePro"]["resolved"], 1)
        self.assertEqual(counts["InvoicePro"]["total"], 2)

    def test_average_resolution_time(self):
        cleaned = self.cleaner.clean_records(self.raw_data)
        analytics = TicketAnalytics.compute_resolution_times(cleaned)

        self.assertEqual(analytics["total_resolved_count"], 2)

        # T1: 09:00 to 14:00 = 5 hours
        # T3: Sep 3 11:00 to Sep 4 09:00 = 22 hours
        # Average = (5 + 22) / 2 = 13.5 hours
        self.assertEqual(analytics["avg_resolution_hours_per_product"]["CloudSync"], 5.0)
        self.assertEqual(analytics["avg_resolution_hours_per_product"]["InvoicePro"], 22.0)
        self.assertEqual(analytics["overall_avg_resolution_hours"], 13.5)


class TestGraphQuery(unittest.TestCase):
    def test_graph_multi_product_customer(self):
        graph = InMemorySupportGraph()
        graph.add_ticket("T1", "Asha Rao", "CloudSync", "Issue 1", "resolved", "2026-09-01T09:00:00", "2026-09-01T14:00:00")
        graph.add_ticket("T2", "Liam Chen", "CloudSync", "Issue 2", "open", "2026-09-02T10:00:00", None)
        graph.add_ticket("T3", "Asha Rao", "InvoicePro", "Issue 3", "resolved", "2026-09-03T11:00:00", "2026-09-04T09:00:00")
        graph.add_ticket("T4", "Priya Nair", "InvoicePro", "Issue 4", "open", "2026-09-05T08:30:00", None)

        results = graph.query_customers_with_multiple_products()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["customer_name"], "Asha Rao")
        self.assertEqual(results[0]["distinct_products_count"], 2)
        self.assertListEqual(results[0]["products"], ["CloudSync", "InvoicePro"])


if __name__ == "__main__":
    unittest.main()
