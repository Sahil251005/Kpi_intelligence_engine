# BusinessIntelligence.ai

### From Metrics to Meaning

BusinessIntelligence.ai is a business intelligence and investigation system that helps understand **why an important business KPI has changed**, rather than only reporting that it changed.

The system combines business data from the Olist e-commerce dataset with additional business context to investigate KPI changes, identify possible drivers, gather supporting evidence, and rank potential explanations with confidence.

The goal is simple: turn a business metric change into a **clear, evidence-based explanation and a practical next step**.

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

## Key Features

* **KPI Anomaly Detection** – Identifies unusual changes that may need investigation.
* **Historical Analysis** – Compares the current KPI behavior with its historical pattern.
* **Driver Analysis** – Breaks down the KPI to understand what is contributing to the change.
* **Business Context** – Uses available context such as inventory, marketing, and KPI targets during the investigation.
* **Evidence Building** – Brings together relevant signals from business data and customer reviews.
* **Hypothesis Generation** – Produces possible explanations for the observed KPI change.
* **Confidence Scoring** – Scores the hypotheses based on the supporting evidence.
* **Uncertainty Handling** – Avoids forcing a conclusion when the available evidence is not strong enough.

## How It Works

The investigation starts with a business case that needs attention and moves through several stages to understand what is happening and how strongly the available evidence supports each possible explanation.

### 1. Select the Investigation Case

The system first identifies the **highest-priority investigation case**, using the available KPI and business context.

### 2. Look at Historical Behavior

For the selected **region and product category**, the system retrieves historical data and compares the current period with previous periods. This helps determine whether the current change is unusual compared with its past behavior.

### 3. Measure the Anomaly

The system calculates **Z-scores** for the relevant metrics to quantify how far the current values are from their historical behavior.

### 4. Build a Hybrid Assessment

The historical analysis and Z-score results are combined with the investigation case to create a broader assessment of the KPI change.

### 5. Build the Evidence

The system brings the results of the analysis together into a structured evidence set. This gives the next stage specific facts to work with rather than asking the model to interpret the raw data directly.

### 6. Generate Possible Hypotheses

The evidence is passed to an LLM to generate a small set of possible explanations. The model is instructed to use **only the supplied evidence**, avoid treating correlation as causation, and clearly identify what is still unknown.

### 7. Analyze the Hypotheses

Each generated hypothesis is further analyzed to identify signals, relationship type, direction, claim type, and whether uncertainty or causal language is present.

### 8. Calculate Confidence

The system evaluates each hypothesis against the available evidence and calculates a **supporting score, weakening score, confidence score, and confidence level**.

### 9. Present the Investigation

The final result brings together the KPI change, supporting evidence, possible explanations, and confidence levels so that the business user can understand **what changed, what may be driving it, and how strongly the evidence supports each explanation**.

### Investigation Flow

**Investigation Case → Historical Analysis → Z-Score Analysis → Hybrid Assessment → Evidence → Hypotheses → NLP Analysis → Confidence**


## Dataset & Experimental Setup

The project uses the **Brazilian Olist e-commerce dataset** as its main source of business data. The raw data includes information about:

* Customers
* Orders
* Order items
* Products
* Sellers
* Payments
* Reviews
* Geolocation
* Product categories

For the experimental setup, we add an **inventory context dataset** in `Data/synthetic/inventory_context.csv`. This provides inventory information that is not available in the original Olist dataset and allows us to study the relationship between inventory changes and KPI changes.

The data is loaded into **PostgreSQL**, where the main business tables are combined with the inventory data and the resulting information is prepared for the investigation pipeline.

The database also maintains investigation-specific data, including the **analytics investigation queue and investigation history**, which are used by the backend when analyzing and comparing investigation cases.

## Technology Stacks

### PostgreSQL & SQL

We use **PostgreSQL** as the main data and analytics layer of the project. The raw e-commerce data is first stored in relational tables, and SQL is then used to join, transform, and prepare that data for the investigation engine.

The flow inside PostgreSQL is:

**Raw Data → Analytics Views → KPI Calculation → Revenue & Inventory Analysis → Business Signals → Investigation Queue**

#### 1. Storing the Business Data

The Olist data is stored in separate tables such as `orders`, `order_items`, `customers`, `products`, and `sellers`. We also add an `inventory_context` table containing the experimental inventory data.

This keeps the original business data organized and allows the different sources to be connected through their relationships.

#### 2. Creating a Combined Analytics View

The `analytics_order_items` view brings together information from orders, order items, customers, products, and sellers into one analytical view.

It also calculates the total value of an item using:

**item total value = price + freight value**

This view gives the analytics layer a convenient starting point without changing the original tables.

#### 3. Calculating the Monthly KPI

The `analytics_monthly_kpi` view aggregates delivered orders by month and calculates:

* **Revenue**
* **Total orders**
* **Items sold**
* **Average order value**

Revenue is calculated from the item prices, while the analysis focuses on delivered orders.

#### 4. Measuring Revenue Anomalies

The `analytics_revenue_anomaly` view compares the current month's revenue with the average revenue from the previous three months.

It calculates:

* Expected revenue
* Revenue deviation percentage
* Historical standard deviation
* **Z-score**
* Anomaly status

The Z-score is then used to classify the revenue movement as normal, moderately positive/negative, or highly positive/negative.

#### 5. Breaking Revenue Down by Region and Category

For the investigation use case, `analytics_revenue_region_category` takes the analysis one step further by calculating revenue separately for each **month, customer region, and product category**.

This gives us a more useful view of where a KPI change is happening instead of looking only at overall revenue.

The `analytics_revenue_driver` view then compares each region-category combination with its previous three-month average and calculates its expected revenue, revenue difference, deviation percentage, and driver status.

#### 6. Adding Inventory Signals

The `analytics_inventory_kpi` view prepares the experimental inventory data by calculating:

* **Stock ratio**
* **Inventory value**
* **Stock change percentage**
* Whether stock is **below the reorder level**

The previous stock level is obtained using the inventory history for the same product category and warehouse.

#### 7. Combining Revenue and Inventory

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

#### 8. Creating the Investigation Queue

Finally, `analytics_investigation_queue` assigns scores to the revenue deviation, inventory change, and reorder status.

These scores are combined into a **priority score**, which is then used to classify cases as:

**HIGH → MEDIUM → LOW**

Only cases with a non-zero priority score are included in the investigation queue.

This queue becomes the starting point for the Python backend, which performs the deeper investigation and confidence analysis.

**In short, PostgreSQL does more than store our data. It takes the raw business data, calculates the KPIs, identifies meaningful revenue and inventory signals, and prepares prioritized cases for the investigation engine.**

### Python Backend

The Python backend takes the investigation cases prepared by PostgreSQL and carries the investigation further. Each file has a specific role, so the analysis is split into smaller steps rather than being handled in one place.

#### `database.py` — Database Connection

This file handles the connection between Python and PostgreSQL.

It:

* Loads the database configuration from the `.env` file.
* Builds the PostgreSQL connection URL using the database credentials.
* Creates a **SQLAlchemy engine** that the other backend functions use to communicate with the database.

The rest of the backend uses this connection whenever it needs to retrieve data from PostgreSQL.

#### `analytics.py` — Investigation Logic

This is the main analytics file in the backend. It takes the investigation data prepared by PostgreSQL and performs the deeper analysis.

It handles four main things:

* **Investigation cases** – Retrieves the investigation queue and selects the highest-priority case.
* **Historical analysis** – Retrieves the previous records for the same region and product category and calculates historical averages and medians for revenue deviation and stock change.
* **Z-score analysis** – Compares the selected case with its historical behavior and calculates Z-scores for revenue deviation and stock change.
* **Evidence & confidence** – Combines the business scores, historical results, and statistical results into a structured evidence package and later evaluates how strongly the evidence supports each hypothesis.

#### `llm.py` — Hypothesis Generation

This file handles the LLM part of the investigation.

The structured evidence produced by the analytics layer is passed to the **Groq API**, which generates possible investigation hypotheses.

The prompt places clear limits on the model. It is instructed to:

* Use only the supplied evidence.
* Avoid inventing causes that are not supported by the data.
* Avoid treating correlation as confirmed causation.
* Separate what is known from what remains unknown.
* Prefer a small number of stronger hypotheses over many speculative ones.

The generated response is also returned in a structured format containing the **hypothesis type, statement, evidence basis, and unknowns**.

#### `nlp.py` — Hypothesis Analysis

This file analyzes the language of each generated hypothesis.

It looks for:

* Business signals such as **revenue and inventory**.
* The type of relationship being described, such as **causal, potential impact, correlation, or descriptive**.
* The type of claim being made.
* Whether the statement indicates a positive, negative, mixed, or neutral direction.
* Whether the statement contains uncertainty or hedging language.

This analysis does **not** decide whether a hypothesis is true. Instead, it extracts these characteristics so they can be considered by the confidence-scoring logic.

#### How the Backend Components Work Together

The backend follows this flow:

**PostgreSQL Investigation Queue**
↓
**`database.py` — Connect to PostgreSQL**
↓
**`analytics.py` — Historical & statistical analysis**
↓
**Evidence Package**
↓
**`llm.py` — Generate hypotheses**
↓
**`nlp.py` — Analyze hypothesis language**
↓
**`analytics.py` — Calculate evidence-based confidence**

Together, these components turn a prioritized KPI case into a structured investigation with **evidence, possible explanations, and confidence scores**.

