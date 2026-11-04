# Part B.1: LLM-Generated Ticket Summaries Evaluation

This document outlines the evaluation framework, scoring methodology, and detailed assessment of the LLM-generated one-line summaries for tickets **T1–T3** compared against reference summaries and ground-truth ticket data.

---

## 1. Evaluation Metric & Rubric Framework

To evaluate summary quality in a production customer support / IT triage setting, summaries cannot merely be judged on grammatical fluency. They must preserve **actionable diagnostic signal** for support engineers while remaining concise.

We define a **Multi-Dimensional Weighted Rubric (Score: 1.0 – 5.0)**:

| Dimension | Weight | Description | Scoring Guide (1 to 5) |
| :--- | :---: | :--- | :--- |
| **1. Factual Accuracy & Faithfulness** | **30%** | Freedom from hallucinations, distortions, or invented details. Must strictly reflect the original ticket issue. | **5**: Fully faithful.<br>**3**: Slight ambiguity.<br>**1**: Contains hallucinations or false claims. |
| **2. Information Completeness (Root Cause & State)** | **35%** | Preservation of key operational context (e.g., triggering condition, failure stage, line items). | **5**: Preserves all vital technical context.<br>**3**: Missing secondary details.<br>**1**: Omitted primary cause/effect. |
| **3. Entity & Product Attribution** | **20%** | Explicitly mentions the relevant product, service, or affected component. | **5**: Product and sub-system named clearly.<br>**3**: Generic component named.<br>**1**: Product completely missing. |
| **4. Conciseness & Triage Utility** | **15%** | One-line brevity, clear phrasing, and immediate readability for on-call engineers. | **5**: Succinct, professional, active voice.<br>**3**: Verbose or over-compressed.<br>**1**: Incoherent or overly cryptic. |

$$\text{Composite Score} = (0.30 \times \text{Accuracy}) + (0.35 \times \text{Completeness}) + (0.20 \times \text{Entity}) + (0.15 \times \text{Utility})$$

---

## 2. Detailed Ticket-by-Ticket Scoring & Analysis

### Ticket T1
- **Raw Issue**: `"Login fails after password reset"` (Product: `CloudSync`)
- **Reference Summary**: `"Customer locked out of CloudSync after resetting their password."`
- **LLM Summary**: `"User cannot log in to CloudSync."`

#### Metric Breakdown:
- **Factual Accuracy (5.0 / 5.0)**: Completely factually accurate. The user cannot log in to CloudSync.
- **Information Completeness (3.0 / 5.0)**: Lost the critical triggering event: *"after resetting their password"*. In authentication troubleshooting, a failure immediately following a password reset strongly implies token invalidation, directory sync delay, or hash salt errors, rather than basic credential entry errors.
- **Entity Attribution (5.0 / 5.0)**: Correctly retained `"CloudSync"`.
- **Conciseness & Utility (4.0 / 5.0)**: Clean and readable, but the omission of the trigger reduces triage precision.

$$\text{T1 Score} = (0.30 \times 5.0) + (0.35 \times 3.0) + (0.20 \times 5.0) + (0.15 \times 4.0) = 1.50 + 1.05 + 1.00 + 0.60 = \mathbf{4.15 / 5.0} \quad (83\%)$$

**Verdict**: Acceptable high-level summary, but sub-optimal for triage due to loss of the temporal causal trigger ("after password reset").

---

### Ticket T2
- **Raw Issue**: `"Sync stuck at 90%"` (Product: `CloudSync`)
- **Reference Summary**: `"CloudSync sync process hangs near completion."`
- **LLM Summary**: `"Sync is stuck."`

#### Metric Breakdown:
- **Factual Accuracy (5.0 / 5.0)**: Factually correct in isolation (the sync operation is stalled).
- **Information Completeness (1.5 / 5.0)**: Severe loss of context. It omitted both the product name and the progress milestone (`90%` / `near completion`). A sync that hangs at `0%` (connection failure) vs. `90%` (finalization, checksum verification, or large file payload) indicates completely different failure modes.
- **Entity Attribution (1.0 / 5.0)**: Completely missing the product entity `"CloudSync"`. In a multi-product ticketing system, a ticket titled "Sync is stuck" cannot be routed to the appropriate engineering queue without opening the ticket.
- **Conciseness & Utility (2.0 / 5.0)**: Over-compressed. Extreme brevity resulted in catastrophic loss of utility.

$$\text{T2 Score} = (0.30 \times 5.0) + (0.35 \times 1.5) + (0.20 \times 1.0) + (0.15 \times 2.0) = 1.50 + 0.525 + 0.20 + 0.30 = \mathbf{2.53 / 5.0} \quad (50.5\%)$$

**Verdict**: Poor summary. Fails essential triage criteria due to missing product context and missing diagnostic specifics.

---

### Ticket T3
- **Raw Issue**: `"PDF export missing line items"` (Product: `InvoicePro`)
- **Reference Summary**: `"InvoicePro-generated PDFs are missing invoice line items."`
- **LLM Summary**: `"PDF export has a missing items bug in InvoicePro."`

#### Metric Breakdown:
- **Factual Accuracy (4.8 / 5.0)**: Accurate and faithful. Characterizing it as a "bug" adds an interpretive noun, but it reflects standard engineering taxonomy.
- **Information Completeness (4.5 / 5.0)**: Captures the subsystem (`PDF export`), the symptom (`missing items`), and the product. Only minor distinction is saying "items" instead of "invoice line items".
- **Entity Attribution (5.0 / 5.0)**: Explicitly names `"InvoicePro"`.
- **Conciseness & Utility (4.8 / 5.0)**: Clear, active, and actionable. An on-call engineer can immediately route this to the billing/document export microservice team.

$$\text{T3 Score} = (0.30 \times 4.8) + (0.35 \times 4.5) + (0.20 \times 5.0) + (0.15 \times 4.8) = 1.44 + 1.575 + 1.00 + 0.72 = \mathbf{4.74 / 5.0} \quad (94.7\%)$$

**Verdict**: Excellent summary. Retains product identity, functional subsystem, and bug characteristics.

---

## 3. Summary Comparison Table

| Ticket ID | Reference Summary | LLM Summary | Accuracy (30%) | Completeness (35%) | Entity (20%) | Utility (15%) | Composite Score | Grade |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **T1** | *Customer locked out of CloudSync after resetting their password.* | *User cannot log in to CloudSync.* | 5.0 / 5 | 3.0 / 5 | 5.0 / 5 | 4.0 / 5 | **4.15 / 5.0** | **B+ (83%)** |
| **T2** | *CloudSync sync process hangs near completion.* | *Sync is stuck.* | 5.0 / 5 | 1.5 / 5 | 1.0 / 5 | 2.0 / 5 | **2.53 / 5.0** | **F (51%)** |
| **T3** | *InvoicePro-generated PDFs are missing invoice line items.* | *PDF export has a missing items bug in InvoicePro.* | 4.8 / 5 | 4.5 / 5 | 5.0 / 5 | 4.8 / 5 | **4.74 / 5.0** | **A (95%)** |

### Key Takeaway for Prompt Engineering:
The primary failure mode observed is **over-compression without entity grounding** (as seen in T2). To prevent this in production:
1. Include explicit system prompt constraints: *"Always retain the product name and specific failure percentages/conditions."*
2. Use few-shot exemplars demonstrating the expected retention of diagnostic triggers.
