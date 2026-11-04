"""
Module: analytics.py
Computes business metrics on cleaned support tickets:
1. Open vs. resolved ticket counts per product
2. Average resolution time in hours for resolved tickets (per product & overall)
"""

from __future__ import annotations
from collections import defaultdict
from typing import Dict, List, Any

try:
    from .data_cleaner import TicketRecord
except ImportError:
    from data_cleaner import TicketRecord



class TicketAnalytics:
    @staticmethod
    def compute_status_counts_per_product(
        records: List[TicketRecord],
    ) -> Dict[str, Dict[str, int]]:
        """
        Computes count of open vs. resolved tickets grouped by product.
        Returns format:
        {
            "CloudSync": {"open": 1, "resolved": 1, "total": 2},
            "InvoicePro": {"open": 1, "resolved": 1, "total": 2}
        }
        """
        product_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"open": 0, "resolved": 0, "total": 0})

        for r in records:
            prod = r.product
            status = r.status.lower()
            if status in ("open", "resolved"):
                product_stats[prod][status] += 1
            else:
                # Capture any other status under its name
                product_stats[prod][status] = product_stats[prod].get(status, 0) + 1
            product_stats[prod]["total"] += 1

        return dict(product_stats)

    @staticmethod
    def compute_resolution_times(
        records: List[TicketRecord],
    ) -> Dict[str, Any]:
        """
        Computes resolution times in hours for resolved tickets:
        - Per-ticket resolution time
        - Average resolution time per product
        - Overall average resolution time across all resolved tickets
        """
        resolved_tickets = [
            r for r in records if r.status == "resolved" and r.resolved_at is not None
        ]

        product_durations: Dict[str, List[float]] = defaultdict(list)
        ticket_durations: List[Dict[str, Any]] = []

        for r in resolved_tickets:
            # created_at and resolved_at are datetime instances
            duration_seconds = (r.resolved_at - r.created_at).total_seconds()
            duration_hours = duration_seconds / 3600.0

            product_durations[r.product].append(duration_hours)
            ticket_durations.append(
                {
                    "ticket_id": r.ticket_id,
                    "product": r.product,
                    "customer": r.customer,
                    "created_at": r.created_at.isoformat(),
                    "resolved_at": r.resolved_at.isoformat(),
                    "resolution_time_hours": round(duration_hours, 2),
                }
            )

        avg_per_product: Dict[str, float] = {}
        for prod, durations in product_durations.items():
            avg_per_product[prod] = round(sum(durations) / len(durations), 2)

        all_durations = [item["resolution_time_hours"] for item in ticket_durations]
        overall_avg = (
            round(sum(all_durations) / len(all_durations), 2)
            if all_durations
            else 0.0
        )

        return {
            "ticket_level_breakdown": ticket_durations,
            "avg_resolution_hours_per_product": avg_per_product,
            "overall_avg_resolution_hours": overall_avg,
            "total_resolved_count": len(resolved_tickets),
        }
