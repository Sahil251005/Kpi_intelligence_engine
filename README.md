# KPI Intelligence Engine

### From KPI Signals to Evidence-Based Business Decisions

KPI Intelligence Engine is an AI-powered business investigation platform that transforms KPI deviations into structured, evidence-backed business insights.

Instead of simply displaying that a KPI has changed, the system investigates how unusual the change is, compares it with historical behavior, identifies supporting evidence, generates an evidence-grounded hypothesis, evaluates confidence, and recommends what should be investigated next.

---

# Problem Statement

Traditional KPI dashboards answer:

> **"What happened?"**

But they often do not answer:

- Why is the KPI changing?
- Is the change actually unusual?
- How does it compare with historical behavior?
- Is the issue isolated to a particular region, category, or warehouse?
- What evidence supports a possible explanation?
- How confident should the business be in that explanation?
- What should be investigated next?

For example:

> Revenue decreased by 25%.

That number alone does not establish whether the decline is normal variation, a genuine anomaly, an inventory-related signal, or something that requires further investigation.

KPI Intelligence Engine addresses this gap by turning KPI anomalies into a structured investigation workflow.

---

# Our Solution

The platform follows an evidence-first investigation process:

**KPI Signal → Historical Context → Statistical Evidence → Business Evidence → Hypothesis → Confidence → Recommendation**

Rather than allowing an AI model to directly guess the cause of a KPI change, the system first constructs an evidence layer and then uses the LLM to generate hypotheses grounded in that evidence.

This makes the investigation more explainable and helps prevent unsupported causal claims.

---

# Key Features

### KPI Anomaly Investigation

Identifies high-priority investigation cases from the KPI investigation queue.

### Historical Baseline Analysis

Compares the current KPI with historical observations for the relevant business dimensions, including region, product category, warehouse, and time period.

### Statistical Anomaly Detection

Uses statistical analysis and z-scores to determine how unusual current KPI behavior is compared with historical patterns.

### Revenue + Inventory Intelligence

The system analyzes revenue and inventory signals together instead of treating them as completely independent metrics.

Example:

```text
Revenue Decline
      +
Rapid Inventory Change
      +
Historical Anomaly
      ↓
High-Priority Investigation
```

### Evidence-Based Investigation

The investigation engine builds structured evidence from:

- Revenue deviation
- Historical KPI behavior
- Inventory movement
- Reorder threshold
- Statistical anomaly status
- Cross-signal relationships
- Business KPI signals

### Evidence-Grounded AI Hypotheses

The LLM generates potential explanations using the available evidence.

The system is designed to avoid inventing unsupported events such as:

- Supplier failures
- Shipment losses
- Fraud
- Operational incidents
- External causes

The generated hypothesis also identifies unknowns where the available evidence is insufficient.

### NLP Hypothesis Interpretation

The generated hypothesis is analyzed to identify:

- Business signals
- Causal language
- Uncertainty
- Investigation language
- Relationships between signals
- Claim types
- Direction of the hypothesis

The NLP layer interprets the hypothesis; it does not independently determine whether the hypothesis is true.

### Confidence

The confidence section communicates how strongly the available evidence supports the investigation.


## Recommendations

The final section presents the recommended next investigation step based on the available evidence.



# Architecture

The application consists of a React and TypeScript frontend connected to a FastAPI backend. The backend coordinates the investigation engine, PostgreSQL data layer, statistical analysis, recommendation logic, NLP processing, and Groq-based LLM hypothesis generation.

# Technology Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- psycopg2

## AI / NLP

- Groq
- LLM-based hypothesis generation
- NLP-based hypothesis interpretation
- Evidence-grounded prompting

## Frontend

- React
- TypeScript
- CSS
- KPI visualization
- Investigation workflow UI

---

# Data Architecture

The platform uses the Olist-based business dataset.

Core business tables include:

- `orders`
- `order_items`
- `customers`
- `products`
- `reviews`
- `payments`
- `sellers`

Supporting tables include:

- `geolocation`
- `product_category_translation`

The project also uses inventory and KPI investigation context for the analytical pipeline.

---

# Project Structure

```text
Kpi_intelligence_engine/
│
├── Backend/
│   ├── analytics.py
│   ├── api.py
│   ├── database.py
│   ├── investigation.py
│   ├── llm.py
│   ├── nlp.py
│   └── recommendation.py
│
├── frontend/
│   └── src/
│       ├── App.tsx
│       └── App.css
│
├── .env
├── requirements.txt
└── README.md
```

---

# API

The backend exposes the investigation service through FastAPI.

### Health / Root

```http
GET /
```

### Investigation

```http
GET /investigation
```

The investigation endpoint returns information required by the dashboard, including:

```text
Case
History
Priority
Key Metrics
Signals
Hypothesis
Confidence
Recommendation
Business Summary
```

---

# Environment Configuration

Create a `.env` file and configure the required credentials:

```env
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name

GROQ_API_KEY=your_groq_api_key
```

Do not commit real credentials or API keys to GitHub.

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/Sahil251005/Kpi_intelligence_engine.git
cd Kpi_intelligence_engine
```

## 2. Create a Python environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

## 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure PostgreSQL

Create and configure the required PostgreSQL database and load the project data.

Then configure the database credentials in `.env`.

---

# Running the Backend

Start the FastAPI server:

```bash
uvicorn Backend.api:app --host 0.0.0.0 --port 8001
```

The API will then be available on port `8001`.

---

# Running the Frontend

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Run the development server:

```bash
npm run dev
```

The frontend communicates with the FastAPI investigation endpoint.

---

# Example Investigation

A typical investigation can contain a context such as:

```text
Region:
SP

Category:
cama_mesa_banho

Warehouse:
SP-Warehouse-1

Period:
July 2018
```

### Revenue Signal

```text
Actual Revenue:    27,106.04
Expected Revenue:  36,306.10
Deviation:         -25.34%
```

### Inventory Signal

```text
Stock:             480
Reorder Threshold: 300
Stock Change:      -56.68%

Status:
RAPID_STOCK_DECLINE
```

### Business Signal

```text
HIGH_PRIORITY_SIGNAL
```

The combined signals produce a high-priority investigation rather than simply displaying the revenue decline as an isolated KPI.

---

# Design Principles

## 1. Evidence Before Explanation

The system does not ask the LLM to directly explain a KPI.

Instead:

```text
Data
 ↓
Analysis
 ↓
Evidence
 ↓
Hypothesis
```

---

## 2. Hypotheses Are Not Facts

AI-generated explanations are treated as hypotheses.

The system preserves uncertainty where the available data cannot establish causality.

---

## 3. No Unsupported Causality

The system avoids statements such as:

> "Supplier delays caused the revenue decline."

unless the available data supports that conclusion.

Instead, the system can identify that observed evidence may be consistent with a particular explanation and specify what remains unknown.

---

## 4. Statistical + Business Reasoning

A KPI should not be considered important simply because its value changed.

The engine combines:

```text
Statistical Evidence
        +
Business Evidence
        +
Historical Context
        ↓
Investigation Priority
```

---

## 5. Actionable Investigation

The final output should help the user determine:

> **What should I investigate next?**

rather than only providing another dashboard metric.

---

# Why This Approach Matters

Traditional analytics often follows:

```text
Data → Dashboard → Human Interpretation
```

KPI Intelligence Engine extends this to:

```text
Data
 ↓
KPI Signal
 ↓
Historical Context
 ↓
Statistical Analysis
 ↓
Evidence
 ↓
AI Hypothesis
 ↓
Confidence
 ↓
Recommended Investigation
```

This creates a bridge between business intelligence and AI-assisted investigation.

---

# Future Enhancements

Potential future improvements include:

- More KPI categories
- Additional operational signals
- Automated root-cause investigation
- More granular warehouse analysis
- Supplier-level evidence
- Customer behavior signals
- Automated anomaly monitoring
- More sophisticated causal analysis
- Investigation history and case tracking
- More role-specific dashboards
- Real-time KPI monitoring

---

# Conclusion

**KPI Intelligence Engine** transforms KPI monitoring from a passive reporting experience into an evidence-driven investigation system.

Instead of stopping at:

> **"Revenue is down."**

the platform attempts to answer:

> **"How unusual is the decline, what evidence supports it, what could explain the behavior, how confident are we, and what should the business investigate next?"**

By combining historical analysis, statistical reasoning, business signals, evidence construction, LLM-powered hypotheses, NLP interpretation, confidence scoring, and actionable recommendations, the system provides a structured path from:

### **Metrics → Evidence → Meaning → Action**
