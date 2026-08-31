# BusinessIntelligence.ai

### From Metrics to Meaning

BusinessIntelligence.ai is an end-to-end KPI investigation platform that goes beyond simply detecting a business metric anomaly. It investigates **why a KPI may have changed**, evaluates the available evidence, generates evidence-grounded hypotheses, assigns confidence, and recommends practical next steps.

The system combines PostgreSQL analytics, Python-based investigation logic, statistical analysis, LLM-assisted hypothesis generation, and a React dashboard to turn a business signal into an explainable investigation.

**Business Signal → Evidence → Hypothesis → Confidence → Action**

---

## Dashboard

The investigation dashboard provides an end-to-end view of a selected business case, from anomaly detection to recommended action.

It brings together KPI performance, historical behavior, statistical evidence, AI-generated hypotheses, confidence assessment, recommended actions, and an executive business summary in a single investigation workflow.

### Investigation Overview

The overview identifies the investigation case and displays the key business indicators:

* Revenue performance
* Inventory movement
* Reorder level
* Investigation priority
* Confidence level
* Region
* Product category
* Warehouse
* Investigation period

### Investigation Flow

The dashboard presents the investigation as a four-stage business flow:

**Signal → Evidence → Hypothesis → Action**

This makes the investigation process understandable from the initial KPI change through to the recommended operational response.

### Historical Performance Trajectory

The dashboard visualizes historical revenue and inventory movement for the selected investigation case.

The investigation month is highlighted so users can compare the current anomaly against previous periods.

### Statistical Evidence

The evidence section presents:

* Inventory movement
* Inventory Z-score
* Revenue deviation
* Dominant business signal

These metrics provide the statistical basis for the investigation.

### AI Investigation Hypothesis

The system presents an evidence-grounded hypothesis explaining the relationship between the observed business signals.

The dashboard explicitly separates:

* What was observed
* What the evidence suggests
* What remains unknown

This prevents the system from presenting a correlation as a confirmed causal relationship.

### Confidence Assessment

The confidence section shows:

* Overall confidence score
* Confidence level
* Supporting evidence score
* Weakening evidence score

The score communicates how strongly the available evidence supports further investigation.

### Recommended Action

The system converts the investigation into an operational recommendation, including:

* Priority
* Confidence
* Signal strength
* Dominant signal
* Reasons supporting the action
* Recommended next steps
* Causal warnings where applicable

### Executive Business Summary

The final section condenses the complete investigation into an executive-friendly summary covering:

* Executive interpretation
* Key evidence
* Investigation hypothesis
* Confidence
* Recommended action
* Important caveats

---

## Problem Statement

Businesses generate large amounts of data from areas such as sales, orders, payments, inventory, and customer feedback. Dashboards can show when an important KPI changes, but understanding **what is driving that change** often requires looking across multiple sources of information.

For example, a change in revenue may be related to factors such as product performance, inventory availability, customer feedback, or regional activity. Finding these connections manually can take time and make it difficult to get a clear picture of what is happening.

The challenge is to move beyond simply detecting a KPI change and build a system that can:

* Identify unusual changes in business metrics.
* Break down the change to find its main drivers.
* Use different business signals to investigate possible causes.
* Compare possible explanations using the available evidence.
* Communicate how confident the system is in those explanations.
* Provide a useful next step while acknowledging when the evidence is not sufficient.

The aim is to turn a KPI change into an **evidence-based investigation**, rather than just another dashboard alert.

---

## Our Solution

BusinessIntelligence.ai takes a KPI change and turns it into a structured investigation. Instead of looking at the metric in isolation, the system brings together different signals from the business data to understand what may be driving the change.

The solution works by:

* **Finding unusual KPI changes** and identifying cases that need investigation.
* **Looking at historical patterns** to understand how the current change compares with previous behavior.
* **Breaking down the KPI** to identify the factors contributing to the change.
* **Using business context** such as inventory, marketing, targets, and other available data to add context to the investigation.
* **Building evidence** from the available structured data and customer review information.
* **Generating possible explanations** for the observed change using the collected evidence.
* **Analyzing and ranking hypotheses** based on the evidence available to the system.
* **Assigning confidence scores** to show how strongly the evidence supports each explanation.
* **Presenting the findings clearly** so that the investigation leads to an understandable business insight rather than just a metric or alert.

The goal is simple:

> **Turn a business metric change into a clear, evidence-based explanation and a practical next step.**

---

## Key Features

* **KPI Anomaly Detection** – Identifies unusual changes that may need investigation.
* **Historical Analysis** – Compares the current KPI behavior with its historical pattern.
* **Driver Analysis** – Breaks down the KPI to understand what is contributing to the change.
* **Business Context** – Uses available context such as inventory, marketing, and KPI targets during the investigation.
* **Evidence Building** – Brings together relevant signals from business data and customer reviews.
* **Hypothesis Generation** – Produces possible explanations for the observed KPI change.
* **Hypothesis Analysis** – Extracts signals, relationship types, direction, and uncertainty from generated hypotheses.
* **Confidence Scoring** – Scores hypotheses based on the supporting and weakening evidence.
* **Recommendation Engine** – Converts investigation findings into practical next steps.
* **Executive Summary** – Condenses the investigation into a business-friendly final interpretation.
* **Uncertainty Handling** – Avoids forcing a conclusion when the available evidence is not strong enough.
* **Interactive Dashboard** – Presents the investigation through a React-based business intelligence interface.
* **Dynamic API Integration** – Dashboard data is retrieved dynamically from the backend investigation API.

---

# How It Works

The investigation starts with a business case that needs attention and moves through several stages to understand what is happening and how strongly the available evidence supports each possible explanation.

### End-to-End Business Flow

**Signal Detection**

↓

**Statistical Evidence**

↓

**Historical Performance**

↓

**AI Investigation Hypothesis**

↓

**Confidence Assessment**

↓

**Recommended Action**

↓

**Executive Business Summary**

---

### 1. Select the Investigation Case

The system first identifies the **highest-priority investigation case**, using the available KPI and business context.

The investigation queue prioritizes cases based on the severity of the observed business signals.

---

### 2. Look at Historical Behavior

For the selected **region and product category**, the system retrieves historical data and compares the current period with previous periods.

This helps determine whether the current change is unusual compared with its past behavior.

---

### 3. Measure the Anomaly

The system calculates **Z-scores** for the relevant metrics to quantify how far the current values are from their historical behavior.

This provides a statistical measure of how unusual the observed movement is.

---

### 4. Build a Hybrid Assessment

The historical analysis and Z-score results are combined with the investigation case to create a broader assessment of the KPI change.

This allows the system to consider both:

* Statistical behavior
* Business context

---

### 5. Build the Evidence

The system brings the results of the analysis together into a structured evidence set.

This gives the next stage specific facts to work with rather than asking the model to interpret raw data directly.

---

### 6. Generate Possible Hypotheses

The structured evidence is passed to an LLM to generate a small set of possible explanations.

The model is instructed to:

* Use only the supplied evidence.
* Avoid inventing causes that are not supported by the data.
* Avoid treating correlation as confirmed causation.
* Separate what is known from what remains unknown.
* Prefer a small number of stronger hypotheses over many speculative ones.

---

### 7. Analyze the Hypotheses

Each generated hypothesis is further analyzed to identify:

* Business signals
* Relationship type
* Claim type
* Direction
* Causal language
* Uncertainty or hedging language

This analysis does **not** decide whether a hypothesis is true.

Instead, it extracts characteristics that can be considered by the confidence-scoring logic.

---

### 8. Calculate Confidence

The system evaluates each hypothesis against the available evidence and calculates:

* Supporting evidence score
* Weakening evidence score
* Confidence score
* Confidence level

The purpose is to communicate how strongly the available evidence supports further investigation.

---

### 9. Recommend an Action

The investigation results are converted into an operational recommendation.

The recommendation includes:

* Investigation priority
* Signal strength
* Dominant signal
* Reasons supporting the action
* Recommended next steps
* Causal warning when evidence is insufficient to establish causation

---

### 10. Present the Investigation

The final result brings together:

**What changed → What evidence was found → What may explain it → How confident we are → What should happen next**

This creates a complete business investigation rather than a simple KPI alert.

---

# Investigation Flow

The technical investigation pipeline can be summarized as:

**Investigation Case → Historical Analysis → Z-Score Analysis → Hybrid Assessment → Evidence → Hypotheses → NLP Analysis → Confidence → Recommendation**

The frontend then presents these results as a business-facing investigation:

**Signal → Evidence → Hypothesis → Confidence → Action**

---

# Dataset & Experimental Setup

The project uses the **Brazilian Olist e-commerce dataset** as its main source of business data.

The raw data includes information about:

* Customers
* Orders
* Order items
* Products
* Sellers
* Payments
* Reviews
* Geolocation
* Product categories

For the experimental setup, we add an **inventory context dataset** in:

`Data/synthetic/inventory_context.csv`

This provides inventory information that is not available in the original Olist dataset and allows us to study the relationship between inventory changes and KPI changes.

The data is loaded into **PostgreSQL**, where the main business tables are combined with the inventory data and the resulting information is prepared for the investigation pipeline.

The database also maintains investigation-specific data, including the **analytics investigation queue and investigation history**, which are used by the backend when analyzing and comparing investigation cases.

---

# Technology Stack

## PostgreSQL & SQL

We use **PostgreSQL** as the main data and analytics layer of the project.

The raw e-commerce data is first stored in relational tables, and SQL is then used to join, transform, and prepare that data for the investigation engine.

The flow inside PostgreSQL is:

**Raw Data → Analytics Views → KPI Calculation → Revenue & Inventory Analysis → Business Signals → Investigation Queue**

---

### 1. Storing the Business Data

The Olist data is stored in separate tables such as:

* `orders`
* `order_items`
* `customers`
* `products`
* `sellers`

We also add an `inventory_context` table containing the experimental inventory data.

This keeps the original business data organized and allows the different sources to be connected through their relationships.

---

### 2. Creating a Combined Analytics View

The `analytics_order_items` view brings together information from orders, order items, customers, products, and sellers into one analytical view.

It also calculates the total value of an item using:

**Item total value = price + freight value**

This view gives the analytics layer a convenient starting point without changing the original tables.

---

### 3. Calculating the Monthly KPI

The `analytics_monthly_kpi` view aggregates delivered orders by month and calculates:

* **Revenue**
* **Total orders**
* **Items sold**
* **Average order value**

Revenue is calculated from the item prices, while the analysis focuses on delivered orders.

---

### 4. Measuring Revenue Anomalies

The `analytics_revenue_anomaly` view compares the current month's revenue with the average revenue from the previous three months.

It calculates:

* Expected revenue
* Revenue deviation percentage
* Historical standard deviation
* **Z-score**
* Anomaly status

The Z-score is then used to classify the revenue movement as normal, moderately positive/negative, or highly positive/negative.

---

### 5. Breaking Revenue Down by Region and Category

For the investigation use case, `analytics_revenue_region_category` takes the analysis one step further by calculating revenue separately for each:

* Month
* Customer region
* Product category

This gives us a more useful view of where a KPI change is happening instead of looking only at overall revenue.

The `analytics_revenue_driver` view then compares each region-category combination with its previous three-month average and calculates:

* Expected revenue
* Revenue difference
* Deviation percentage
* Driver status

---

### 6. Adding Inventory Signals

The `analytics_inventory_kpi` view prepares the experimental inventory data by calculating:

* **Stock ratio**
* **Inventory value**
* **Stock change percentage**
* Whether stock is **below the reorder level**

The previous stock level is obtained using the inventory history for the same product category and warehouse.

---

### 7. Combining Revenue and Inventory

The `analytics_business_signal` view brings the revenue and inventory analysis together.

It connects the two using:

* Month
* Product category
* Region and corresponding warehouse location

The combined data is then used to identify signals such as:

* `CRITICAL_STOCK`
* `RAPID_STOCK_DECLINE`
* `MODERATE_STOCK_DECLINE`
* `INVENTORY_RISK`
* `HIGH_PRIORITY_SIGNAL`
* `MODERATE_PRIORITY_SIGNAL`

This is where separate KPI and inventory changes start becoming a business investigation signal.

---

### 8. Creating the Investigation Queue

Finally, `analytics_investigation_queue` assigns scores to:

* Revenue deviation
* Inventory change
* Reorder status

These scores are combined into a **priority score**, which is then used to classify cases as:

**HIGH → MEDIUM → LOW**

Only cases with a non-zero priority score are included in the investigation queue.

This queue becomes the starting point for the Python backend, which performs the deeper investigation and confidence analysis.

---

### PostgreSQL in Summary

PostgreSQL does more than store our data.

It takes the raw business data, calculates the KPIs, identifies meaningful revenue and inventory signals, and prepares prioritized cases for the investigation engine.

**Raw Business Data → KPI Analytics → Business Signals → Investigation Queue**

---

# Python Backend

The Python backend takes the investigation cases prepared by PostgreSQL and carries the investigation further.

Each file has a specific role, so the analysis is split into smaller steps rather than being handled in one place.

---

## `database.py` — Database Connection

This file handles the connection between Python and PostgreSQL.

It:

* Loads the database configuration from the `.env` file.
* Builds the PostgreSQL connection URL using the database credentials.
* Creates a **SQLAlchemy engine** that the other backend functions use to communicate with the database.

The rest of the backend uses this connection whenever it needs to retrieve data from PostgreSQL.

---

## `investigation.py` — Investigation Pipeline

This file orchestrates the complete investigation process.

It handles the major investigation stages including:

* Investigation case selection
* Historical analysis
* Statistical analysis
* Evidence construction
* Business signal assessment
* Hypothesis evaluation
* Confidence scoring
* Recommendation generation
* Executive business summary

The purpose of this layer is to connect the outputs of the data and analytics layer into a structured investigation result.

---

## `llm.py` — Hypothesis Generation

This file handles the LLM part of the investigation.

The structured evidence produced by the investigation layer is passed to the **Groq API**, which generates possible investigation hypotheses.

The prompt places clear limits on the model.

It is instructed to:

* Use only the supplied evidence.
* Avoid inventing causes that are not supported by the data.
* Avoid treating correlation as confirmed causation.
* Separate what is known from what remains unknown.
* Prefer a small number of stronger hypotheses over many speculative ones.

The generated response is returned in a structured format containing the hypothesis statement, evidence basis, and unknowns.

---

## `nlp.py` — Hypothesis Analysis

This file analyzes the language of each generated hypothesis.

It looks for:

* Business signals such as **revenue and inventory**.
* The type of relationship being described, such as **causal, potential impact, correlation, or descriptive**.
* The type of claim being made.
* Whether the statement indicates a positive, negative, mixed, or neutral direction.
* Whether the statement contains uncertainty or hedging language.

This analysis does **not** decide whether a hypothesis is true.

Instead, it extracts these characteristics so they can be considered by the confidence-scoring logic.

---

# React Frontend

The frontend is built using **React, TypeScript, Vite, and Recharts**.

It provides an interactive dashboard for consuming and presenting the investigation generated by the backend.

The dashboard dynamically renders:

* Investigation overview
* KPI cards
* Investigation flow
* Historical revenue/inventory trajectory
* Statistical evidence
* AI investigation hypothesis
* Confidence assessment
* Recommended actions
* Next steps
* Executive business summary

The frontend is driven by the backend investigation response rather than hardcoded investigation results.

---

## Frontend Investigation Sections

### Investigation Overview

Displays the selected investigation case along with:

* Region
* Category
* Warehouse
* Investigation period
* Revenue
* Inventory
* Reorder level
* Priority
* Confidence

---

### Historical Signal Movement

The dashboard plots historical revenue and inventory movement for the selected case.

The investigation month is explicitly highlighted so users can understand how the current period compares with previous observations.

---

### Statistical Evidence

Displays the main statistical signals behind the investigation:

* Inventory movement
* Inventory Z-score
* Revenue deviation
* Dominant business signal

---

### AI Investigation Hypothesis

Displays the evidence-grounded hypothesis generated from the investigation evidence.

The interface separates evidence from interpretation and explicitly communicates remaining uncertainty.

---

### Confidence Assessment

Displays the confidence score and its supporting and weakening factors.

The purpose is not to claim that a cause has been proven, but to communicate whether the available evidence is strong enough to justify further investigation.

---

### Recommended Action

Displays:

* Priority
* Confidence
* Signal strength
* Dominant signal
* Reasons for the recommendation
* Next steps
* Causal warning

This converts analytical output into an operational business response.

---

### Executive Business Summary

The final dashboard section summarizes the complete investigation for an executive audience.

It covers:

1. Executive Summary
2. Key Evidence
3. Investigation Hypothesis
4. Confidence
5. Recommended Action
6. Important Caveat

---

# API

The backend exposes the investigation engine through a FastAPI endpoint.

## GET `/investigation`

The endpoint returns the complete investigation result, including:

* Investigation case
* Historical records
* Priority
* Key metrics
* Business signals
* Selected hypothesis
* Confidence assessment
* Recommendation
* Executive business summary

The response is consumed directly by the React frontend.

### Response Structure

```json
{
  "case": {},
  "history": [],
  "priority": {},
  "key_metrics": {},
  "signals": {},
  "hypothesis": {},
  "confidence": {},
  "recommendation": {},
  "business_summary": {}
}

---

#Team

### Team Commit & Conquer

* [Kanishka Sakunia](https://github.com/kanishka5268)
* [Chiranjeev Kalyane](https://github.com/CJK2710Sec)
* [Sahil Sutar](https://github.com/Sahil251005)


