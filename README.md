# BusinessIntelligence.ai

## From Metrics to Meaning

BusinessIntelligence.ai is an end-to-end KPI investigation platform that goes beyond detecting business metric anomalies.

Instead of simply showing that a KPI changed, the system investigates **what changed, what evidence supports the change, what may explain it, how strong the evidence is, and what should happen next**.

The platform combines PostgreSQL analytics, Python-based investigation logic, statistical analysis, LLM-assisted hypothesis generation, NLP analysis, and a React dashboard.

### Core Flow

**Business Signal → Evidence → Hypothesis → Confidence → Action**

---

# Problem Statement

Business dashboards are effective at showing **what happened**, but understanding **why it happened** often requires manually analyzing multiple data sources.

A change in revenue, for example, may be related to inventory availability, product performance, regional activity, customer feedback, or other business factors.

The challenge is to move beyond KPI monitoring and build a system that can:

- Identify unusual KPI movements.
- Find where the change is concentrated.
- Analyze relevant business drivers.
- Build evidence from multiple signals.
- Generate possible explanations.
- Evaluate supporting and weakening evidence.
- Communicate uncertainty.
- Recommend practical next steps.

The objective is to transform a KPI change into an **evidence-based investigation rather than a simple dashboard alert**.

---

# Our Solution

BusinessIntelligence.ai takes a business KPI signal and turns it into a structured investigation.

The system:

1. Detects unusual KPI behavior.
2. Compares current performance with historical behavior.
3. Identifies important revenue and inventory signals.
4. Builds structured evidence from the available data.
5. Generates evidence-grounded hypotheses using an LLM.
6. Analyzes hypothesis relationships, direction, and uncertainty.
7. Calculates confidence from supporting and weakening evidence.
8. Produces an operational recommendation.
9. Presents the complete investigation through an interactive dashboard.

### Investigation Philosophy

> **Evidence can justify an investigation without proving causation.**

The system therefore distinguishes between:

- **Observed** — what the data directly shows.
- **Suggested** — what the evidence makes plausible.
- **Unknown** — what the available evidence cannot establish.

This prevents the platform from presenting correlation as confirmed causation.

---

# Key Features

- **KPI Anomaly Detection** — Identifies unusual business movements.
- **Historical Analysis** — Compares current behavior with historical patterns.
- **Driver Analysis** — Breaks down KPI changes by region and product category.
- **Inventory Context** — Adds inventory and reorder signals to the investigation.
- **Statistical Evidence** — Uses deviations and Z-scores to quantify unusual behavior.
- **Evidence Building** — Converts analytical results into structured evidence.
- **AI Hypothesis Generation** — Produces evidence-grounded explanations.
- **Hypothesis Analysis** — Extracts relationships, direction, claim types, and uncertainty.
- **Confidence Scoring** — Balances supporting and weakening evidence.
- **Recommendation Engine** — Converts investigation findings into practical next steps.
- **Uncertainty Handling** — Avoids unsupported causal conclusions.
- **Interactive Dashboard** — Presents the complete investigation in a business-friendly interface.
- **Historical Visualization** — Displays revenue and inventory movement over time.
- **Executive Outcome** — Provides an immediate summary of what happened, why it matters, and what to do.
- **Executive Business Summary** — Provides a concise final business interpretation.
- **Dynamic API Integration** — Frontend results are retrieved dynamically from the backend.

---

# Dashboard

The dashboard is designed around the same investigation philosophy as the backend.

### Dashboard Flow

**Investigation Case → KPI Snapshot → Investigation Outcome → Signal → Evidence → Hypothesis → Confidence → Action → Executive Summary**

### Investigation Overview

The overview identifies the selected investigation case and displays:

- Investigation period
- Region
- Product category
- Warehouse
- Revenue
- Inventory
- Reorder level
- Investigation priority
- Confidence

### Investigation Outcome

A concise executive layer answers three questions immediately:

**What happened?**

Revenue and inventory movement are summarized using the key KPI deviations.

**Why does it matter?**

The dominant business signal and its statistical strength are highlighted.

**What should happen next?**

The recommended operational investigation is presented without requiring the user to inspect every analytical detail.

The section also communicates when causation remains unconfirmed.

### Investigation Flow

The dashboard presents the reasoning process as:

**Signal → Evidence → Hypothesis → Action**

This makes the investigation understandable to both technical and business users.

### Historical Signal Movement

Revenue and inventory movement are visualized across historical periods.

The investigation month is highlighted so users can compare the current anomaly with previous behavior.

### Statistical Evidence

The dashboard presents the main statistical signals behind the investigation, including:

- Revenue deviation
- Inventory movement
- Inventory Z-score
- Dominant business signal

### AI Investigation Hypothesis

The dashboard presents an evidence-grounded explanation generated from the structured investigation evidence.

It separates:

- What was observed.
- What the evidence suggests.
- What remains unknown.

### Confidence Assessment

The confidence section communicates:

- Overall confidence score
- Confidence level
- Supporting evidence score
- Weakening evidence score

Confidence represents the strength of the available evidence, not proof of causation.

### Recommended Action

The recommendation section translates the investigation into operational validation steps.

It provides:

- Reasons supporting the recommendation.
- Specific next steps.
- Causal warnings where appropriate.

### Executive Business Summary

The final section condenses the investigation into an executive-friendly record covering:

1. Executive interpretation
2. Key evidence
3. Investigation hypothesis
4. Recommended action
5. Important caveat

---

# How It Works

## End-to-End Investigation Pipeline

**Investigation Case**

↓

**Historical Analysis**

↓

**Z-Score Analysis**

↓

**Hybrid Assessment**

↓

**Evidence Construction**

↓

**Hypothesis Generation**

↓

**NLP Hypothesis Analysis**

↓

**Confidence Scoring**

↓

**Recommendation**

↓

**Executive Business Summary**

---

## 1. Investigation Case Selection

The system identifies high-priority cases using KPI and business signals prepared by the PostgreSQL analytics layer.

Cases are prioritized based on the severity of revenue movement, inventory movement, and reorder-level conditions.

---

## 2. Historical Analysis

For the selected region and product category, historical data is retrieved and compared with the investigation period.

This establishes how unusual the current behavior is relative to previous periods.

---

## 3. Statistical Analysis

The system calculates Z-scores and KPI deviations to quantify unusual behavior.

These measurements provide the statistical foundation for the investigation.

---

## 4. Hybrid Assessment

Historical behavior, statistical results, and business context are combined to determine the dominant signal and overall investigation strength.

---

## 5. Evidence Construction

The investigation results are converted into structured evidence.

The LLM receives this structured evidence rather than raw database information, reducing unsupported interpretation.

---

## 6. Hypothesis Generation

The structured evidence is passed to an LLM to generate possible explanations.

The model is instructed to:

- Use only supplied evidence.
- Avoid unsupported causes.
- Avoid treating correlation as confirmed causation.
- Separate known information from unknowns.
- Prefer stronger explanations over speculative ones.

---

## 7. Hypothesis Analysis

Generated hypotheses are analyzed for:

- Business signals
- Relationship type
- Claim type
- Direction
- Causal language
- Uncertainty or hedging language

This stage describes the hypothesis rather than determining whether it is true.

---

## 8. Confidence Scoring

The investigation evaluates supporting and weakening evidence to calculate:

- Supporting evidence score
- Weakening evidence score
- Confidence score
- Confidence level

---

## 9. Recommendation

The investigation is translated into an operational recommendation containing:

- Investigation priority
- Signal strength
- Dominant signal
- Supporting reasons
- Recommended next steps
- Causal warning where appropriate

---

# Dataset & Experimental Setup

The project uses the **Brazilian Olist e-commerce dataset** as its primary business dataset.

The dataset contains information about:

- Customers
- Orders
- Order items
- Products
- Sellers
- Payments
- Reviews
- Geolocation
- Product categories

An additional synthetic inventory dataset is used to introduce inventory context that is not available in the original Olist dataset:

`Data/synthetic/inventory_context.csv`

This provides inventory information such as stock levels, reorder levels, and inventory movement for the investigation experiment.

The data is loaded into PostgreSQL and combined through analytical views for KPI, revenue, inventory, and business-signal analysis.

---

# Technology Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Database | PostgreSQL |
| Analytics | SQL / PostgreSQL Views |
| Backend | FastAPI |
| Database Connectivity | SQLAlchemy |
| AI | Groq API / LLM |
| NLP | Python |
| Frontend | React |
| Frontend Language | TypeScript |
| Build Tool | Vite |
| Visualization | Recharts |
| Data Processing | Pandas |
| Version Control | Git / GitHub |

---

# PostgreSQL & SQL Analytics

PostgreSQL acts as the primary data and analytics layer.

### Main Tables

- `orders`
- `order_items`
- `customers`
- `products`
- `sellers`
- `inventory_context`

### Analytics Pipeline

**Raw Data → Analytics Views → KPI Calculation → Revenue & Inventory Analysis → Business Signals → Investigation Queue**

### Important Analytics Views

- `analytics_order_items`
- `analytics_monthly_kpi`
- `analytics_revenue_anomaly`
- `analytics_revenue_region_category`
- `analytics_revenue_driver`
- `analytics_inventory_kpi`
- `analytics_business_signal`
- `analytics_investigation_queue`

The analytics layer calculates revenue performance, historical expectations, revenue deviations, inventory movement, reorder conditions, and investigation priority.

---

# Python Backend

The Python backend performs the deeper investigation after PostgreSQL prepares the prioritized cases.

## `database.py`

Handles the PostgreSQL connection.

It:

- Loads database configuration from `.env`.
- Builds the database connection.
- Creates the SQLAlchemy engine used by the backend.

## `investigation.py`

Orchestrates the complete investigation pipeline:

- Case selection
- Historical analysis
- Statistical analysis
- Evidence construction
- Hypothesis evaluation
- Confidence scoring
- Recommendation generation
- Executive summary generation

## `llm.py`

Handles LLM-assisted hypothesis generation through the Groq API.

The LLM receives structured evidence and is constrained to avoid unsupported explanations and unverified causal claims.

The system also includes deterministic fallback behavior when the LLM service is unavailable.

## `nlp.py`

Analyzes generated hypotheses for:

- Business signals
- Relationship type
- Claim type
- Direction
- Causal language
- Uncertainty

The extracted characteristics contribute to the investigation and confidence logic.

---

# React Frontend

The frontend is built using:

- React
- TypeScript
- Vite
- Recharts

The dashboard consumes the FastAPI investigation response dynamically.

The frontend presents:

- Investigation overview
- KPI snapshot
- Investigation outcome
- Investigation flow
- Historical performance trajectory
- Statistical evidence
- AI hypothesis
- Confidence assessment
- Recommended action
- Executive business summary

The interface is designed to keep **evidence, interpretation, uncertainty, and action clearly separated**.

---

# API

The backend exposes the investigation through FastAPI.

## `GET /investigation`

Returns the complete investigation result:

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

```
---
# Running the Project

## Backend

Activate the virtual environment and start the FastAPI server:

```bash
uvicorn Backend.api:app --reload --port 8001
```
The investigation API will be available at:

```text
http://127.0.0.1:8001/investigation
```

## Frontend

Navigate to the frontend directory and install the dependencies:

```bash
cd frontend
npm install
npm run dev
```

The Vite development server will provide the dashboard locally.

---

### Team Commit & Conquer

* [Kanishka Sakunia](https://github.com/kanishka5268)
* [Chiranjeev Kalyane](https://github.com/CJK2710Sec)
* [Sahil Sutar](https://github.com/Sahil251005)


