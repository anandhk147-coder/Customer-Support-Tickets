// ==============================================================================
// PART B.2: Neo4j Graph Model & Cypher Queries
// Domain: Customer Support Tickets & Product Lineage
// ==============================================================================

// ------------------------------------------------------------------------------
// STEP 1: Schema Constraints & Indexes (Best Practice for Performance & Idempotency)
// ------------------------------------------------------------------------------

CREATE CONSTRAINT unique_customer_name IF NOT EXISTS
FOR (c:Customer) REQUIRE c.name IS UNIQUE;

CREATE CONSTRAINT unique_ticket_id IF NOT EXISTS
FOR (t:Ticket) REQUIRE t.ticket_id IS UNIQUE;

CREATE CONSTRAINT unique_product_name IF NOT EXISTS
FOR (p:Product) REQUIRE p.name IS UNIQUE;


// ------------------------------------------------------------------------------
// STEP 2: Graph Ingestion (Cleaned Dataset from Part A)
// Pattern: (:Customer)-[:RAISED]->(:Ticket)-[:ABOUT]->(:Product)
// ------------------------------------------------------------------------------

// Ingest Ticket T1
MERGE (c1:Customer {name: "Asha Rao"})
MERGE (p1:Product {name: "CloudSync"})
MERGE (t1:Ticket {ticket_id: "T1"})
ON CREATE SET 
    t1.issue = "Login fails after password reset",
    t1.status = "resolved",
    t1.created_at = datetime("2026-09-01T09:00:00"),
    t1.resolved_at = datetime("2026-09-01T14:00:00")
MERGE (c1)-[:RAISED]->(t1)
MERGE (t1)-[:ABOUT]->(p1);

// Ingest Ticket T2
MERGE (c2:Customer {name: "Liam Chen"})
MERGE (p2:Product {name: "CloudSync"})
MERGE (t2:Ticket {ticket_id: "T2"})
ON CREATE SET 
    t2.issue = "Sync stuck at 90%",
    t2.status = "open",
    t2.created_at = datetime("2026-09-02T10:00:00"),
    t2.resolved_at = null
MERGE (c2)-[:RAISED]->(t2)
MERGE (t2)-[:ABOUT]->(p2);

// Ingest Ticket T3
MERGE (c3:Customer {name: "Asha Rao"})
MERGE (p3:Product {name: "InvoicePro"})
MERGE (t3:Ticket {ticket_id: "T3"})
ON CREATE SET 
    t3.issue = "PDF export missing line items",
    t3.status = "resolved",
    t3.created_at = datetime("2026-09-03T11:00:00"),
    t3.resolved_at = datetime("2026-09-04T09:00:00")
MERGE (c3)-[:RAISED]->(t3)
MERGE (t3)-[:ABOUT]->(p3);

// Ingest Ticket T4 (Handling missing issue with standard placeholder)
MERGE (c4:Customer {name: "Priya Nair"})
MERGE (p4:Product {name: "InvoicePro"})
MERGE (t4:Ticket {ticket_id: "T4"})
ON CREATE SET 
    t4.issue = "[Issue description not provided]",
    t4.status = "open",
    t4.created_at = datetime("2026-09-05T08:30:00"),
    t4.resolved_at = null
MERGE (c4)-[:RAISED]->(t4)
MERGE (t4)-[:ABOUT]->(p4);


// ------------------------------------------------------------------------------
// STEP 3: THE TARGET QUERY
// "Write a query that finds every customer who has raised a ticket about more 
//  than one distinct product."
// ------------------------------------------------------------------------------

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

// ------------------------------------------------------------------------------
// ALTERNATIVE PRODUCTION-OPTIMIZED FORMULATION (Subquery / Pattern Comprehension)
// Suitable for high-scale graphs to avoid early Cartesian expansion
// ------------------------------------------------------------------------------
/*
MATCH (c:Customer)
WHERE COUNT {
    MATCH (c)-[:RAISED]->(:Ticket)-[:ABOUT]->(p:Product)
    RETURN DISTINCT p
} > 1
RETURN c.name AS customer_name;
*/
