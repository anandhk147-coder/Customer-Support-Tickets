# Customer Support Tickets: Data Pipeline, LLM Evaluation & Knowledge Graph

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-Cypher-008CC1.svg)](https://neo4j.com/)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)]()

Production-grade implementation for the **Set 1: Customer Support Tickets** take-home assessment, covering:
1. **Part A (Data Pipeline & Analytics)**: Cleaning, deduplication, schema validation, missing value imputation, and metric computation.
2. **Part B.1 (LLM Evals)**: Multi-dimensional evaluation rubric (Accuracy, Completeness, Entity Attribution, Utility) scoring LLM summaries vs. ground truth.
3. **Part B.2 (Knowledge Graph with Neo4j)**: Graph modeling (`Customer —raised→ Ticket —about→ Product`) and Cypher query for multi-product customers.

---

## 📁 Repository Structure

```
customer-support-tickets/
├── README.md                      # Comprehensive project documentation & results
├── requirements.txt               # Optional dependencies (neo4j, pytest)
├── .gitignore
├── data/
│   ├── raw_tickets.json           # Raw input dataset
│   └── cleaned_tickets.json       # Deduplicated & sanitized dataset
├── part_a/
│   ├── __init__.py
│   ├── data_cleaner.py            # Deduplication, validation & missing-value handling
│   ├── analytics.py               # Ticket counting and resolution time computations
│   └── run_part_a.py              # CLI executable for Part A pipeline
├── part_b/
│   ├── __init__.py
│   ├── evaluation_rubric.md       # Full rubric & qualitative evaluation writeup
│   ├── evaluate_summaries.py      # Automated scoring & token overlap calculator
│   ├── neo4j_queries.cypher       # DDL constraints, MERGE ingestion & Cypher queries
│   └── graph_simulation.py        # Graph engine & query runner (live Neo4j + in-memory)
└── tests/
    ├── __init__.py
    └── test_pipeline.py           # Unit test suite (100% pass rate)
```

---

## 🚀 Quickstart

The entire core pipeline uses the **Python Standard Library** with zero mandatory external dependencies.

```bash
# 1. Clone repository
git clone <your-repo-url>
cd customer-support-tickets

# 2. Run All Pipelines, Checks & Tests in CLI
python main.py

# 3. Launch the Interactive Web Dashboard (Local Host)
python dashboard/server.py
# Then open http://localhost:8000 in your browser!
```

---

## 📊 Summary of Results

### Part A: Data Cleaning & Analytics

#### 1. Data Cleaning Actions Taken:
- **Deduplication**: Detected and pruned duplicate record `T1` (exact row duplicate).
- **Missing Field Handling**: Handled ticket `T4` which had an empty string `issue: ""`. Replaced with placeholder `"[Issue description not provided]"` and flagged for data observability.
- **Timestamp Integrity**: Validated ISO-8601 parsing and ensured `resolved_at` is present for resolved tickets and null for open tickets.

#### 2. Metric 1: Open vs. Resolved Ticket Count per Product
| Product | Open Tickets | Resolved Tickets | Total Tickets |
| :--- | :---: | :---: | :---: |
| **CloudSync** | 1 (`T2`) | 1 (`T1`) | 2 |
| **InvoicePro** | 1 (`T4`) | 1 (`T3`) | 2 |

#### 3. Metric 2: Resolution Time for Resolved Tickets
| Ticket ID | Customer | Product | Created At | Resolved At | Duration |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **T1** | Asha Rao | CloudSync | `2026-09-01T09:00:00` | `2026-09-01T14:00:00` | **5.00 hours** |
| **T3** | Asha Rao | InvoicePro | `2026-09-03T11:00:00` | `2026-09-04T09:00:00` | **22.00 hours** |

- **CloudSync Average Resolution Time**: **5.00 hours**
- **InvoicePro Average Resolution Time**: **22.00 hours**
- **Overall Average Resolution Time**: **13.50 hours** $\left(\frac{5 + 22}{2} = 13.5\text{ hrs}\right)$

---

### Part B.1: LLM-Generated Summary Evaluation

#### Scoring Rubric (1.0 to 5.0 scale):
$$\text{Composite Score} = (0.30 \times \text{Accuracy}) + (0.35 \times \text{Completeness}) + (0.20 \times \text{Entity}) + (0.15 \times \text{Utility})$$

| Ticket ID | Reference Summary | LLM Summary | Accuracy (30%) | Completeness (35%) | Entity (20%) | Utility (15%) | Composite Score | Grade |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **T1** | *Customer locked out of CloudSync after resetting their password.* | *User cannot log in to CloudSync.* | 5.0 | 3.0 | 5.0 | 4.0 | **4.15 / 5.0** | **B+ (83%)** |
| **T2** | *CloudSync sync process hangs near completion.* | *Sync is stuck.* | 5.0 | 1.5 | 1.0 | 2.0 | **2.53 / 5.0** | **F (51%)** |
| **T3** | *InvoicePro-generated PDFs are missing invoice line items.* | *PDF export has a missing items bug in InvoicePro.* | 4.8 | 4.5 | 5.0 | 4.8 | **4.74 / 5.0** | **A (95%)** |

#### Key Justifications:
1. **T1**: Factually sound, but lost the temporal trigger (*"after resetting their password"*). In identity and support triage, post-reset lockouts indicate cache/token invalidation issues rather than forgotten credentials.
2. **T2**: Suffers from catastrophic over-compression. It omits the product (`CloudSync`) and the progress state (`90%` / `near completion`), rendering it impossible to route or prioritize without reading the full ticket.
3. **T3**: Excellent summary. Accurately captured product (`InvoicePro`), sub-feature (`PDF export`), and the specific symptom (`missing items`).

*(See [part_b/evaluation_rubric.md](part_b/evaluation_rubric.md) for full rubric details.)*

---

### Part B.2: Knowledge Graph (Neo4j)

#### Graph Schema:
- **Nodes**:
  - `(:Customer {name: STRING})`
  - `(:Ticket {ticket_id: STRING, issue: STRING, status: STRING, created_at: DATETIME, resolved_at: DATETIME})`
  - `(:Product {name: STRING})`
- **Edges**:
  - `(:Customer)-[:RAISED]->(:Ticket)`
  - `(:Ticket)-[:ABOUT]->(:Product)`

#### Cypher Query:
Find every customer who has raised a ticket about **more than one distinct product**:

```cypher
MATCH (c:Customer)-[:RAISED]->(t:Ticket)-[:ABOUT]->(p:Product)
WITH c, 
     count(DISTINCT p) AS distinct_products_count, 
     collect(DISTINCT p.name) AS products,
     collect(t.ticket_id) AS tickets_raised
WHERE distinct_products_count > 1
RETURN c.name AS customer_name, 
       distinct_products_count, 
       products,
       tickets_raised
ORDER BY distinct_products_count DESC, customer_name ASC;
```

#### Query Execution Output:
```text
+---------------+-------------------------+----------------------------+----------------+
| customer_name | distinct_products_count | products                   | tickets_raised |
+---------------+-------------------------+----------------------------+----------------+
| "Asha Rao"    | 2                       | ["CloudSync", "InvoicePro"]| ["T1", "T3"]   |
+---------------+-------------------------+----------------------------+----------------+
1 row returned.
```

*(Liam Chen only raised a ticket for `CloudSync`; Priya Nair only raised a ticket for `InvoicePro`.)*

---

## 🛠️ Unit Tests

The test suite validates:
- Deduplication and handling of primary key collisions.
- Missing field replacement and sanitization.
- Accurate calculation of status counts and resolution hours.
- Graph traversal logic and filtering for multi-product customers.

Run tests:
```bash
python -m unittest discover tests
```
Output:
```text
Ran 5 tests in 0.010s
OK
```
