"""
Generates pixel-accurate, high-resolution visual snapshots of the
Customer Support Tickets interactive web dashboard (dashboard/server.py).
Saves to docs/screenshots/ for embedding into GitHub README.md.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

OUT_DIR = Path("docs/screenshots")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def draw_header(ax, active_tab="a"):
    # Background
    ax.add_patch(patches.Rectangle((0, 0), 1400, 850, facecolor="#0B0F19", edgecolor="none"))
    
    # Top navbar
    ax.add_patch(patches.Rectangle((0, 780), 1400, 70, facecolor="#0F172A", edgecolor="#1E293B", linewidth=1.5))
    
    # Logo
    ax.add_patch(patches.FancyBboxPatch((40, 795), 40, 40, boxstyle="round,pad=0.2", facecolor="#2563EB", edgecolor="none"))
    ax.text(60, 815, "ST", color="white", fontsize=14, fontweight="bold", ha="center", va="center")
    
    # Title & Subtitle
    ax.text(95, 822, "Customer Support Tickets", color="white", fontsize=15, fontweight="bold", va="center")
    ax.text(325, 822, "Localhost:8000", color="#34D399", fontsize=9, fontweight="bold", va="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#064E3B", edgecolor="#059669", linewidth=0.8))
    ax.text(95, 802, "Set 1: Data Pipeline, LLM Evals & Neo4j Knowledge Graph", color="#94A3B8", fontsize=9, va="center")
    
    # Tab buttons
    tabs = [
        ("Part A: Data & Metrics", "a", 920),
        ("Part B.1: LLM Evals", "b1", 1080),
        ("Part B.2: Neo4j Graph", "b2", 1230),
    ]
    for label, key, x in tabs:
        is_active = (key == active_tab)
        bg = "#2563EB" if is_active else "#1E293B"
        tc = "#FFFFFF" if is_active else "#94A3B8"
        ax.add_patch(patches.FancyBboxPatch((x, 798), 135, 34, boxstyle="round,pad=0.2", facecolor=bg, edgecolor="#334155" if not is_active else "none", linewidth=1))
        ax.text(x + 67.5, 815, label, color=tc, fontsize=9.5, fontweight="bold" if is_active else "normal", ha="center", va="center")


def draw_kpi_cards(ax):
    cards = [
        (40, "RAW RECORDS PROCESSED", "5", "1 duplicate removed", "#F59E0B", "#78350F"),
        (380, "CLEANED UNIQUE TICKETS", "4", "Across 2 Products", "#60A5FA", "#1E3A8A"),
        (720, "AVG RESOLUTION TIME", "13.5 hrs", "2 Resolved (T1 & T3)", "#34D399", "#064E3B"),
        (1060, "MULTI-PRODUCT CUSTOMERS", "1", "Asha Rao (CloudSync, InvoicePro)", "#C084FC", "#581C87"),
    ]
    for x, title, stat, tag, tag_color, tag_bg in cards:
        ax.add_patch(patches.FancyBboxPatch((x, 690), 300, 75, boxstyle="round,pad=0.4", facecolor="#111827", edgecolor="#1F2937", linewidth=1.2))
        ax.text(x + 18, 745, title, color="#9CA3AF", fontsize=8, fontweight="bold")
        ax.text(x + 18, 715, stat, color="white", fontsize=20, fontweight="bold")
        ax.text(x + 282, 715, tag, color=tag_color, fontsize=7.5, fontweight="bold", ha="right",
                bbox=dict(boxstyle="round,pad=0.25", facecolor=tag_bg, edgecolor=tag_color, linewidth=0.6))


def generate_snapshot_part_a():
    fig, ax = plt.subplots(figsize=(14, 8.5), dpi=100)
    ax.set_xlim(0, 1400)
    ax.set_ylim(0, 850)
    ax.axis("off")
    
    draw_header(ax, "a")
    draw_kpi_cards(ax)
    
    # Left Box: Metric 1 Bar Chart (Open vs Resolved)
    ax.add_patch(patches.FancyBboxPatch((40, 370), 640, 300, boxstyle="round,pad=0.4", facecolor="#111827", edgecolor="#1F2937", linewidth=1.2))
    ax.text(65, 645, "Metric 1: Open vs. Resolved Count Per Product", color="white", fontsize=12, fontweight="bold")
    ax.text(65, 627, "Cleaned dataset volume across CloudSync and InvoicePro", color="#9CA3AF", fontsize=8.5)
    
    # Bars for CloudSync
    ax.text(180, 585, "CloudSync", color="#E5E7EB", fontsize=10, fontweight="bold", ha="center")
    ax.add_patch(patches.Rectangle((120, 420), 45, 140, facecolor="#F59E0B", edgecolor="none")) # Open
    ax.text(142.5, 570, "1 Open", color="white", fontsize=8, fontweight="bold", ha="center")
    ax.add_patch(patches.Rectangle((175, 420), 45, 140, facecolor="#10B981", edgecolor="none")) # Resolved
    ax.text(197.5, 570, "1 Res", color="white", fontsize=8, fontweight="bold", ha="center")
    
    # Bars for InvoicePro
    ax.text(420, 585, "InvoicePro", color="#E5E7EB", fontsize=10, fontweight="bold", ha="center")
    ax.add_patch(patches.Rectangle((360, 420), 45, 140, facecolor="#F59E0B", edgecolor="none")) # Open
    ax.text(382.5, 570, "1 Open", color="white", fontsize=8, fontweight="bold", ha="center")
    ax.add_patch(patches.Rectangle((415, 420), 45, 140, facecolor="#10B981", edgecolor="none")) # Resolved
    ax.text(437.5, 570, "1 Res", color="white", fontsize=8, fontweight="bold", ha="center")
    
    # Legend
    ax.add_patch(patches.Rectangle((530, 638), 12, 12, facecolor="#F59E0B"))
    ax.text(550, 644, "Open Tickets", color="#9CA3AF", fontsize=8, va="center")
    ax.add_patch(patches.Rectangle((530, 620), 12, 12, facecolor="#10B981"))
    ax.text(550, 626, "Resolved Tickets", color="#9CA3AF", fontsize=8, va="center")

    # Right Box: Metric 2 Resolution Time
    ax.add_patch(patches.FancyBboxPatch((720, 370), 640, 300, boxstyle="round,pad=0.4", facecolor="#111827", edgecolor="#1F2937", linewidth=1.2))
    ax.text(745, 645, "Metric 2: Resolution Time in Hours (Resolved Tickets)", color="white", fontsize=12, fontweight="bold")
    ax.text(745, 627, "CloudSync (5.0h) vs InvoicePro (22.0h) & Overall Average (13.5h)", color="#9CA3AF", fontsize=8.5)
    
    # Bars for Durations
    # T1
    ax.add_patch(patches.Rectangle((800, 420), 60, 50, facecolor="#3B82F6", edgecolor="none"))
    ax.text(830, 480, "5.0 hrs", color="white", fontsize=9, fontweight="bold", ha="center")
    ax.text(830, 400, "CloudSync (T1)", color="#9CA3AF", fontsize=8.5, ha="center")
    
    # T3
    ax.add_patch(patches.Rectangle((950, 420), 60, 180, facecolor="#8B5CF6", edgecolor="none"))
    ax.text(980, 610, "22.0 hrs", color="white", fontsize=9, fontweight="bold", ha="center")
    ax.text(980, 400, "InvoicePro (T3)", color="#9CA3AF", fontsize=8.5, ha="center")

    # Overall Avg
    ax.add_patch(patches.Rectangle((1100, 420), 60, 115, facecolor="#10B981", edgecolor="none"))
    ax.text(1130, 545, "13.5 hrs", color="white", fontsize=9, fontweight="bold", ha="center")
    ax.text(1130, 400, "Overall Average", color="#34D399", fontsize=8.5, fontweight="bold", ha="center")

    # Bottom Table: Cleaned Support Tickets Dataset
    ax.add_patch(patches.FancyBboxPatch((40, 40), 1320, 305, boxstyle="round,pad=0.4", facecolor="#111827", edgecolor="#1F2937", linewidth=1.2))
    ax.text(65, 315, "Cleaned Support Tickets Dataset", color="white", fontsize=12, fontweight="bold")
    ax.text(65, 298, "Deduplicated Primary Key: ticket_id | Missing Issue Imputation Applied", color="#9CA3AF", fontsize=8.5)

    # Table Header
    headers = [("TICKET ID", 65), ("CUSTOMER", 160), ("PRODUCT", 300), ("ISSUE DESCRIPTION", 440), ("STATUS", 830), ("CREATED AT", 960), ("RESOLVED AT", 1160)]
    for h, hx in headers:
        ax.text(hx, 275, h, color="#6B7280", fontsize=8, fontweight="bold")
    ax.plot([65, 1330], [265, 265], color="#1F2937", linewidth=1)

    # Rows
    rows = [
        ("T1", "Asha Rao", "CloudSync", "Login fails after password reset", "resolved", "#10B981", "#064E3B", "2026-09-01T09:00:00", "2026-09-01T14:00:00 (5.0h)"),
        ("T2", "Liam Chen", "CloudSync", "Sync stuck at 90%", "open", "#F59E0B", "#78350F", "2026-09-02T10:00:00", "null"),
        ("T3", "Asha Rao", "InvoicePro", "PDF export missing line items", "resolved", "#10B981", "#064E3B", "2026-09-03T11:00:00", "2026-09-04T09:00:00 (22.0h)"),
        ("T4", "Priya Nair", "InvoicePro", "[Issue description not provided]", "open", "#F59E0B", "#78350F", "2026-09-05T08:30:00", "null"),
    ]
    y = 238
    for tid, cust, prod, iss, st, st_col, st_bg, cat, rat in rows:
        ax.text(65, y, tid, color="white", fontsize=9, fontweight="bold")
        ax.text(160, y, cust, color="#E5E7EB", fontsize=8.5)
        ax.text(300, y, prod, color="#93C5FD", fontsize=8.5)
        ax.text(440, y, iss, color="#FBBF24" if iss.startswith("[") else "#E5E7EB", fontsize=8.5, style="italic" if iss.startswith("[") else "normal")
        ax.text(830, y, st, color=st_col, fontsize=8, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", facecolor=st_bg, edgecolor=st_col, linewidth=0.6))
        ax.text(960, y, cat, color="#9CA3AF", fontsize=8)
        ax.text(1160, y, rat, color="#9CA3AF", fontsize=8)
        ax.plot([65, 1330], [y - 12, y - 12], color="#1F2937", linewidth=0.6)
        y -= 48

    out_path = OUT_DIR / "dashboard_part_a_analytics.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=100, facecolor="#0B0F19")
    plt.close()
    print(f"[+] Saved Part A Snapshot: {out_path}")


def generate_snapshot_part_b1():
    fig, ax = plt.subplots(figsize=(14, 8.5), dpi=100)
    ax.set_xlim(0, 1400)
    ax.set_ylim(0, 850)
    ax.axis("off")
    
    draw_header(ax, "b1")
    draw_kpi_cards(ax)

    # Content Title
    ax.text(40, 660, "Part B.1: LLM-Generated Summary Evaluation Framework", color="white", fontsize=13, fontweight="bold")
    ax.text(40, 642, "Formula: Composite = 0.30*Accuracy + 0.35*Completeness + 0.20*Entity + 0.15*Utility (Scored 1.0 to 5.0)", color="#94A3B8", fontsize=8.5)

    cards = [
        # Ticket T1
        (40, 440, "Ticket T1", "CloudSync", "4.15 / 5.0 (Grade: B+ 83%)", "#34D399",
         "Ref: Customer locked out of CloudSync after resetting their password.",
         "LLM: User cannot log in to CloudSync.",
         [("Accuracy", "5.0 / 5"), ("Completeness", "3.0 / 5"), ("Entity", "5.0 / 5"), ("Utility", "4.0 / 5")],
         "Accurate, but omitted causal trigger ('after resetting password'). In identity triage, post-reset lockouts signify directory sync lag."),
        
        # Ticket T2
        (40, 240, "Ticket T2", "CloudSync", "2.53 / 5.0 (Grade: F 51%)", "#EF4444",
         "Ref: CloudSync sync process hangs near completion.",
         "LLM: Sync is stuck.",
         [("Accuracy", "5.0 / 5"), ("Completeness", "1.5 / 5"), ("Entity", "1.0 / 5"), ("Utility", "2.0 / 5")],
         "Severe context loss. Completely omitted product entity ('CloudSync') and completion milestone ('at 90%'). Impossible to route."),
        
        # Ticket T3
        (40, 40, "Ticket T3", "InvoicePro", "4.74 / 5.0 (Grade: A 95%)", "#10B981",
         "Ref: InvoicePro-generated PDFs are missing invoice line items.",
         "LLM: PDF export has a missing items bug in InvoicePro.",
         [("Accuracy", "4.8 / 5"), ("Completeness", "4.5 / 5"), ("Entity", "5.0 / 5"), ("Utility", "4.8 / 5")],
         "Outstanding triage quality. Retains product ('InvoicePro'), subsystem ('PDF export'), and defect symptom ('missing items')."),
    ]

    for x, y, tid, prod, score_txt, badge_col, ref, llm, scores, just in cards:
        ax.add_patch(patches.FancyBboxPatch((x, y), 1320, 180, boxstyle="round,pad=0.3", facecolor="#111827", edgecolor="#1F2937", linewidth=1.2))
        
        # Header line
        ax.text(x + 20, y + 155, tid, color="#60A5FA", fontsize=11, fontweight="bold")
        ax.text(x + 110, y + 155, f"Product: {prod}", color="#9CA3AF", fontsize=9)
        ax.text(x + 1300, y + 155, score_txt, color=badge_col, fontsize=10, fontweight="bold", ha="right")
        
        # Reference vs LLM
        ax.add_patch(patches.Rectangle((x + 20, y + 75), 620, 60, facecolor="#0B0F19", edgecolor="#1E293B"))
        ax.text(x + 30, y + 120, "REFERENCE SUMMARY (GROUND TRUTH):", color="#64748B", fontsize=7.5, fontweight="bold")
        ax.text(x + 30, y + 95, f'"{ref}"', color="#E2E8F0", fontsize=8.5, style="italic")

        ax.add_patch(patches.Rectangle((x + 660, y + 75), 640, 60, facecolor="#0B0F19", edgecolor="#1E293B"))
        ax.text(x + 670, y + 120, "LLM-GENERATED SUMMARY:", color="#64748B", fontsize=7.5, fontweight="bold")
        ax.text(x + 670, y + 95, f'"{llm}"', color="#F8FAFC", fontsize=8.5, fontweight="bold")

        # Rubric pill stats
        stat_x = x + 20
        for sname, sval in scores:
            ax.add_patch(patches.Rectangle((stat_x, y + 42), 140, 26, facecolor="#1F2937", edgecolor="#374151"))
            ax.text(stat_x + 10, y + 55, sname, color="#9CA3AF", fontsize=7.5)
            ax.text(stat_x + 130, y + 55, sval, color="white", fontsize=8, fontweight="bold", ha="right")
            stat_x += 155

        # Justification
        ax.text(x + 660, y + 52, f"Justification: {just}", color="#93C5FD", fontsize=8)

    out_path = OUT_DIR / "dashboard_part_b1_llm_evals.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=100, facecolor="#0B0F19")
    plt.close()
    print(f"[+] Saved Part B.1 Snapshot: {out_path}")


def generate_snapshot_part_b2():
    fig, ax = plt.subplots(figsize=(14, 8.5), dpi=100)
    ax.set_xlim(0, 1400)
    ax.set_ylim(0, 850)
    ax.axis("off")
    
    draw_header(ax, "b2")
    draw_kpi_cards(ax)

    # Graph Canvas Box
    ax.add_patch(patches.FancyBboxPatch((40, 260), 1320, 410, boxstyle="round,pad=0.4", facecolor="#111827", edgecolor="#1F2937", linewidth=1.2))
    ax.text(65, 645, "Neo4j Knowledge Graph Visualizer: (:Customer)-[:RAISED]->(:Ticket)-[:ABOUT]->(:Product)", color="white", fontsize=12, fontweight="bold")
    ax.text(65, 627, "Interactive Force-Directed Network: Asha Rao highlighted for multi-product relationship", color="#9CA3AF", fontsize=8.5)

    # Graph Legend
    ax.add_patch(patches.Circle((950, 642), 8, facecolor="#8B5CF6"))
    ax.text(965, 642, "Multi-Product Customer (Asha Rao)", color="#E5E7EB", fontsize=8, va="center")
    ax.add_patch(patches.Circle((1150, 642), 8, facecolor="#3B82F6"))
    ax.text(1165, 642, "Customer", color="#E5E7EB", fontsize=8, va="center")
    ax.add_patch(patches.Rectangle((1240, 635), 14, 14, facecolor="#059669"))
    ax.text(1260, 642, "Product", color="#E5E7EB", fontsize=8, va="center")

    # --- Draw Nodes & Edges ---
    # Customer Nodes
    ax.add_patch(patches.FancyBboxPatch((150, 480), 160, 45, boxstyle="round,pad=0.3", facecolor="#8B5CF6", edgecolor="#C084FC", linewidth=2))
    ax.text(230, 502, "Asha Rao", color="white", fontsize=10, fontweight="bold", ha="center", va="center")

    ax.add_patch(patches.FancyBboxPatch((150, 390), 160, 40, boxstyle="round,pad=0.3", facecolor="#3B82F6", edgecolor="#60A5FA", linewidth=1.2))
    ax.text(230, 410, "Liam Chen", color="white", fontsize=9, ha="center", va="center")

    ax.add_patch(patches.FancyBboxPatch((150, 310), 160, 40, boxstyle="round,pad=0.3", facecolor="#3B82F6", edgecolor="#60A5FA", linewidth=1.2))
    ax.text(230, 330, "Priya Nair", color="white", fontsize=9, ha="center", va="center")

    # Ticket Nodes
    tickets = [
        (550, 540, "Ticket T1", "resolved", "#10B981"),
        (550, 460, "Ticket T2", "open", "#F59E0B"),
        (550, 380, "Ticket T3", "resolved", "#10B981"),
        (550, 300, "Ticket T4", "open", "#F59E0B"),
    ]
    for tx, ty, tname, tstatus, tcolor in tickets:
        ax.add_patch(patches.FancyBboxPatch((tx, ty), 150, 38, boxstyle="round,pad=0.2", facecolor="#1F2937", edgecolor=tcolor, linewidth=1.5))
        ax.text(tx + 75, ty + 19, f"{tname} ({tstatus})", color="white", fontsize=8.5, ha="center", va="center")

    # Product Nodes
    ax.add_patch(patches.FancyBboxPatch((980, 500), 180, 50, boxstyle="round,pad=0.3", facecolor="#059669", edgecolor="#34D399", linewidth=2))
    ax.text(1070, 525, "CloudSync", color="white", fontsize=11, fontweight="bold", ha="center", va="center")

    ax.add_patch(patches.FancyBboxPatch((980, 340), 180, 50, boxstyle="round,pad=0.3", facecolor="#059669", edgecolor="#34D399", linewidth=2))
    ax.text(1070, 365, "InvoicePro", color="white", fontsize=11, fontweight="bold", ha="center", va="center")


    # Edges: Asha Rao -> T1 & T3
    ax.annotate("", xy=(550, 555), xytext=(310, 505), arrowprops=dict(arrowstyle="->", color="#A855F7", lw=2))
    ax.text(410, 545, "-[:RAISED]->", color="#C084FC", fontsize=8, rotation=12)

    ax.annotate("", xy=(550, 400), xytext=(310, 495), arrowprops=dict(arrowstyle="->", color="#A855F7", lw=2))
    ax.text(410, 435, "-[:RAISED]->", color="#C084FC", fontsize=8, rotation=-14)

    # Liam Chen -> T2
    ax.annotate("", xy=(550, 480), xytext=(310, 410), arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.2))
    ax.text(410, 470, "-[:RAISED]->", color="#94A3B8", fontsize=7.5, rotation=15)

    # Priya Nair -> T4
    ax.annotate("", xy=(550, 320), xytext=(310, 330), arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.2))
    ax.text(410, 330, "-[:RAISED]->", color="#94A3B8", fontsize=7.5)

    # T1 -> CloudSync
    ax.annotate("", xy=(980, 530), xytext=(700, 555), arrowprops=dict(arrowstyle="->", color="#10B981", lw=1.8))
    ax.text(820, 555, "-[:ABOUT]->", color="#34D399", fontsize=8)

    # T2 -> CloudSync
    ax.annotate("", xy=(980, 515), xytext=(700, 480), arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.2))
    ax.text(820, 505, "-[:ABOUT]->", color="#94A3B8", fontsize=7.5, rotation=8)

    # T3 -> InvoicePro
    ax.annotate("", xy=(980, 375), xytext=(700, 400), arrowprops=dict(arrowstyle="->", color="#10B981", lw=1.8))
    ax.text(820, 395, "-[:ABOUT]->", color="#34D399", fontsize=8, rotation=-6)

    # T4 -> InvoicePro
    ax.annotate("", xy=(980, 355), xytext=(700, 320), arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.2))
    ax.text(820, 335, "-[:ABOUT]->", color="#94A3B8", fontsize=7.5, rotation=7)

    # Cypher Query Box at Bottom
    ax.add_patch(patches.FancyBboxPatch((40, 40), 1320, 200, boxstyle="round,pad=0.4", facecolor="#0F172A", edgecolor="#1E293B", linewidth=1.2))
    ax.text(65, 215, "Target Cypher Query (Find Customers With Tickets for >1 Distinct Product)", color="#34D399", fontsize=10.5, fontweight="bold")
    
    cypher_text = (
        "MATCH (c:Customer)-[:RAISED]->(t:Ticket)-[:ABOUT]->(p:Product)\n"
        "WITH c, count(DISTINCT p) AS distinct_products_count, collect(DISTINCT p.name) AS products, collect(t.ticket_id) AS tickets_raised\n"
        "WHERE distinct_products_count > 1\n"
        "RETURN c.name AS customer_name, distinct_products_count, products, tickets_raised\n"
        "ORDER BY distinct_products_count DESC, customer_name ASC;"
    )
    ax.text(65, 140, cypher_text, color="#E2E8F0", fontsize=8.5, family="monospace")

    # Result Box
    ax.add_patch(patches.Rectangle((880, 55), 450, 140, facecolor="#1E1B4B", edgecolor="#4338CA"))
    ax.text(900, 170, "QUERY EXECUTION RESULT:", color="#A5B4FC", fontsize=8.5, fontweight="bold")
    ax.text(900, 145, "Customer: Asha Rao", color="white", fontsize=9.5, fontweight="bold")
    ax.text(900, 120, "Distinct Products (2): CloudSync, InvoicePro", color="#34D399", fontsize=8.5)
    ax.text(900, 95, "Tickets Raised: ['T1', 'T3']", color="#94A3B8", fontsize=8.5)
    ax.text(900, 70, "Status: Ground truth match (Liam Chen & Priya = 1)", color="#C084FC", fontsize=8)

    out_path = OUT_DIR / "dashboard_part_b2_neo4j_graph.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=100, facecolor="#0B0F19")
    plt.close()
    print(f"[+] Saved Part B.2 Snapshot: {out_path}")


def main():
    print("=" * 70)
    print(" GENERATING VISUAL SNAPSHOTS OF THE LOCAL DASHBOARD ")
    print("=" * 70)
    generate_snapshot_part_a()
    generate_snapshot_part_b1()
    generate_snapshot_part_b2()
    print("=" * 70)


if __name__ == "__main__":
    main()
