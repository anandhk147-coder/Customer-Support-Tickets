"""
Module: data_cleaner.py
Provides robust data cleaning, deduplication, schema validation,
and missing field handling for support ticket records.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class TicketRecord:
    ticket_id: str
    customer: str
    product: str
    issue: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        d["resolved_at"] = self.resolved_at.isoformat() if self.resolved_at else None
        return d


class TicketDataCleaner:
    """
    Cleans raw customer ticket datasets:
    - Deduplicates records by primary key (ticket_id) and/or deep record equality.
    - Handles missing/empty fields (e.g., blank issues, missing customer names).
    - Validates datetime parsing and status consistency (resolved vs resolved_at).
    """

    DEFAULT_ISSUE_PLACEHOLDER = "[Issue description not provided]"
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

    def __init__(self, issue_placeholder: str = DEFAULT_ISSUE_PLACEHOLDER):
        self.issue_placeholder = issue_placeholder
        self.cleaning_stats = {
            "total_raw_records": 0,
            "exact_duplicates_removed": 0,
            "id_duplicates_removed": 0,
            "missing_issues_handled": 0,
            "invalid_records_skipped": 0,
            "cleaned_records_count": 0,
        }

    @classmethod
    def parse_iso_datetime(cls, dt_str: Optional[str]) -> Optional[datetime]:
        if not dt_str or not isinstance(dt_str, str):
            return None
        # Support standard ISO formats including trailing Z
        clean_str = dt_str.replace("Z", "")
        return datetime.fromisoformat(clean_str)

    def clean_records(self, raw_records: List[Dict[str, Any]]) -> List[TicketRecord]:
        """
        Cleans, validates, and deduplicates the list of ticket dictionaries.
        """
        self.cleaning_stats["total_raw_records"] = len(raw_records)
        seen_ticket_ids: Dict[str, Dict[str, Any]] = {}
        cleaned_list: List[TicketRecord] = []

        for idx, row in enumerate(raw_records):
            ticket_id = (row.get("ticket_id") or "").strip()
            if not ticket_id:
                logger.warning("Row %d missing 'ticket_id', skipping.", idx)
                self.cleaning_stats["invalid_records_skipped"] += 1
                continue

            # Deduplication Check
            if ticket_id in seen_ticket_ids:
                prev_row = seen_ticket_ids[ticket_id]
                if prev_row == row:
                    logger.info("Exact duplicate ticket '%s' skipped.", ticket_id)
                    self.cleaning_stats["exact_duplicates_removed"] += 1
                else:
                    logger.warning(
                        "Duplicate ticket_id '%s' found with differing content. Skipping redundant entry.",
                        ticket_id,
                    )
                    self.cleaning_stats["id_duplicates_removed"] += 1
                continue

            seen_ticket_ids[ticket_id] = row

            # Missing / Blank field handling
            customer = (row.get("customer") or "").strip()
            if not customer:
                customer = "Unknown Customer"

            product = (row.get("product") or "").strip()
            if not product:
                product = "Unknown Product"

            raw_issue = (row.get("issue") or "").strip()
            if not raw_issue:
                issue = self.issue_placeholder
                self.cleaning_stats["missing_issues_handled"] += 1
                logger.info(
                    "Ticket '%s' had empty issue; replaced with placeholder: '%s'",
                    ticket_id,
                    issue,
                )
            else:
                issue = raw_issue

            raw_status = (row.get("status") or "").strip().lower()
            if raw_status not in ("open", "resolved", "in_progress", "closed"):
                raw_status = "open"

            # Parse timestamps
            try:
                created_at = self.parse_iso_datetime(row.get("created_at"))
                if not created_at:
                    raise ValueError("created_at is required")
            except Exception as e:
                logger.error("Failed to parse created_at for ticket '%s': %s", ticket_id, e)
                self.cleaning_stats["invalid_records_skipped"] += 1
                continue

            resolved_at = self.parse_iso_datetime(row.get("resolved_at"))

            # Consistency checks
            if raw_status == "resolved" and not resolved_at:
                logger.warning(
                    "Ticket '%s' marked 'resolved' but resolved_at is null. Setting to created_at as fallback.",
                    ticket_id,
                )
                resolved_at = created_at
            elif raw_status == "open" and resolved_at:
                logger.warning(
                    "Ticket '%s' marked 'open' but has resolved_at timestamp. Correcting status to 'resolved'.",
                    ticket_id,
                )
                raw_status = "resolved"

            record = TicketRecord(
                ticket_id=ticket_id,
                customer=customer,
                product=product,
                issue=issue,
                status=raw_status,
                created_at=created_at,
                resolved_at=resolved_at,
            )
            cleaned_list.append(record)

        self.cleaning_stats["cleaned_records_count"] = len(cleaned_list)
        return cleaned_list
