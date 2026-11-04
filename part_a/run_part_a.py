"""
CLI entrypoint to run Part A:
1. Loads raw tickets from data/raw_tickets.json
2. Cleans duplicates and handles missing fields
3. Saves cleaned data to data/cleaned_tickets.json
4. Computes open vs resolved count per product
5. Computes average resolution time in hours for resolved tickets
"""

import json
import sys
from pathlib import Path

# Add project root and module directory to path
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "part_a"))

from data_cleaner import TicketDataCleaner
from analytics import TicketAnalytics



def main():
    base_dir = Path(__file__).resolve().parent.parent
    raw_path = base_dir / "data" / "raw_tickets.json"
    clean_path = base_dir / "data" / "cleaned_tickets.json"

    print("=" * 70)
    print(" PART A: SUPPORT TICKET DATA CLEANING & ANALYTICS ")
    print("=" * 70)

    # 1. Load raw data
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    print(f"[*] Loaded {len(raw_data)} raw records from: {raw_path}")

    # 2. Clean data
    cleaner = TicketDataCleaner()
    cleaned_records = cleaner.clean_records(raw_data)

    print("\n[+] Data Cleaning Summary:")
    for k, v in cleaner.cleaning_stats.items():
        print(f"    - {k}: {v}")

    # Save cleaned output
    cleaned_dicts = [r.to_dict() for r in cleaned_records]
    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_dicts, f, indent=2)
    print(f"\n[+] Cleaned records saved to: {clean_path}")

    # 3. Compute Metrics
    print("\n" + "=" * 70)
    print(" COMPUTED METRIC 1: Open vs. Resolved Ticket Count per Product")
    print("=" * 70)
    product_counts = TicketAnalytics.compute_status_counts_per_product(cleaned_records)
    print(f"{'Product':<15} | {'Open':<8} | {'Resolved':<10} | {'Total':<8}")
    print("-" * 50)
    for prod, counts in product_counts.items():
        print(f"{prod:<15} | {counts['open']:<8} | {counts['resolved']:<10} | {counts['total']:<8}")

    print("\n" + "=" * 70)
    print(" COMPUTED METRIC 2: Average Resolution Time in Hours (Resolved Tickets)")
    print("=" * 70)
    res_analytics = TicketAnalytics.compute_resolution_times(cleaned_records)

    print("\nIndividual Resolved Tickets Breakdown:")
    for t in res_analytics["ticket_level_breakdown"]:
        print(
            f"  - Ticket {t['ticket_id']} ({t['product']}) | Customer: {t['customer']}\n"
            f"    Created: {t['created_at']} -> Resolved: {t['resolved_at']}\n"
            f"    Duration: {t['resolution_time_hours']} hours\n"
        )

    print("Average Resolution Time Per Product:")
    for prod, avg_h in res_analytics["avg_resolution_hours_per_product"].items():
        print(f"  - {prod}: {avg_h:.2f} hours")

    print(f"\nOverall Average Resolution Time (All Products): {res_analytics['overall_avg_resolution_hours']:.2f} hours")
    print("=" * 70)


if __name__ == "__main__":
    main()
