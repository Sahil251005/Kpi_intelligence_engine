import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceDot,
  ReferenceLine,
  Legend,
} from "recharts";
import "./App.css";

type InvestigationScenario =
  | "priority"
  | "limited"
  | "insufficient";

type HistoryRecord = {
  month: string;
  region: string;
  product_category_name: string;
  revenue: number;
  expected_revenue: number;
  revenue_deviation_pct: number;
  current_stock: number;
  reorder_level: number;
  stock_change_pct: number;
  inventory_status: string;
  business_signal: string;
  priority_score: number;
  priority_level: string;
};

type Persona = "EXECUTIVE" | "OPERATIONS";

type Investigation = {
  case: {
    month: string;
    region: string;
    category: string;
    warehouse: string;
  };

  evidence_sufficiency: {
    status: "SUFFICIENT" | "LIMITED" | "INSUFFICIENT" | "UNKNOWN";
    baseline_months: number;
    minimum_required: number;
    reasons: string[];
  };

  history: HistoryRecord[];

  priority: {
    score: number;
    level: string;
  };

  key_metrics: {
    revenue: {
      actual: number;
      expected: number;
      deviation_pct: number;
      z_score: number | null;
    };

    inventory: {
      current_stock: number;
      reorder_level: number;
      stock_change_pct: number;
      z_score: number | null;
      status: string;
      below_reorder: boolean;
    };
  };

  signals: {
    revenue_declined: boolean;
    inventory_declined: boolean;
    dominant_signal: string;
  };

  hypothesis: {
    type: string;
    statement: string;
  };

  confidence: {
    score: number;
    level: string;
    supporting_score: number;
    weakening_score: number;
  };

  recommendation: {
    action: string;
    urgency: string;
    priority: string;
    priority_score: number;

    confidence: {
      score: number;
      level: string;
    };

    reason: string[];
    weakening_factors: string[];
    next_steps: string[];
    confidence_note: string;
    causal_warning: string | null;
    signal_strength: number;
  };

  business_summary: string;
};

function getSummarySection(
  summary: string,
  sectionNumber: number
): string {
  if (!summary) return "";

  // Normalize line endings
  const text = summary.replace(/\r\n/g, "\n").trim();

  // Match numbered markdown headings such as:
  // **1. Executive Summary**
  // 1. Executive Summary
  const headingRegex =
    /^\s*\**(\d+)\.\s+(.+?)\**\s*$/gm;

  const headings = [...text.matchAll(headingRegex)];

  if (headings.length === 0) {
    return "";
  }

  const currentIndex = headings.findIndex(
    (match) => Number(match[1]) === sectionNumber
  );

  if (currentIndex === -1) {
    return "";
  }

  const currentHeading = headings[currentIndex];

  const start = currentHeading.index! + currentHeading[0].length;

  const end =
    currentIndex + 1 < headings.length
      ? headings[currentIndex + 1].index!
      : text.length;

  return text
    .slice(start, end)
    .replace(/\*\*/g, "")
    .replace(/^\s*[-•]\s*/gm, "")
    .trim();
}

function App() {

  const [persona, setPersona] =
    useState<Persona>("EXECUTIVE");

  const [scenario, setScenario] =
    useState<InvestigationScenario>("priority");

  const [investigation, setInvestigation] =
    useState<Investigation | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [running, setRunning] =
    useState(false);

  const runInvestigation = async () => {
    try {
      setRunning(true);
      setError("");

      const scenarioParam =
        scenario === "priority"
          ? ""
          : `?scenario=${scenario}`;

      const response = await fetch(
        `http://127.0.0.1:8001/investigation${scenarioParam}`
      );

      if (!response.ok) {
        throw new Error(
          "Investigation request failed"
        );
      }

      const data: Investigation = await response.json();


      setInvestigation(data);
      setError("");

    } catch (err) {
      console.error(
        "Investigation request failed:",
        err
      );

      /*
       * Only show the error screen when
       * there is no valid investigation available.
       */
      if (!investigation) {
        setError(
          "Unable to connect to the investigation engine."
        );
      }

    } finally {
      setLoading(false);
      setRunning(false);
    }
  };

  useEffect(() => {
    runInvestigation();
  }, [scenario]);

  if (loading) {
    return (
      <div className="app loading-screen">
        <div className="loader" />

        <p>
          Running investigation...
        </p>
      </div>
    );
  }

  if (error && !investigation) {
    return (
      <div className="app error-screen">
        <h1>
          Investigation Engine Offline
        </h1>

        <p>{error}</p>

        <span>
          Make sure FastAPI is running on port
          8001.
        </span>
      </div>
    );
  }

  if (!investigation) {
    return null;
  }

  const isExecutive = persona === "EXECUTIVE";

  const scenarioContent = {
    priority: {
      heroEyebrow: "INVESTIGATION REQUIRED",

      heroDescription:
        "A high-priority business signal requires attention across revenue and inventory performance.",

      outcomeTitle:
        "Revenue and inventory declined together.",

      outcomeDescription:
        "Inventory is the dominant business signal and requires validation against operational activity.",

      hypothesisTitle:
        "Evidence supports investigation",

      confidenceTitle:
        "Evidence supports the investigation, but uncertainty remains.",

      summaryStatus:
        "INVESTIGATION COMPLETE",
    },

    limited: {
      heroEyebrow: "LIMITED EVIDENCE",

      heroDescription:
        "A business signal has been detected, but the available historical baseline is limited.",

      outcomeTitle:
        "The signal is visible, but the historical baseline is thin.",

      outcomeDescription:
        "The investigation can identify a direction, but confidence is deliberately constrained by limited historical evidence.",

      hypothesisTitle:
        "Evidence suggests a possible driver",

      confidenceTitle:
        "The evidence points toward a driver, but limited history constrains confidence.",

      summaryStatus:
        "LIMITED EVIDENCE",
    },

    insufficient: {
      heroEyebrow:
        "EVIDENCE INSUFFICIENT",

      heroDescription:
        "A business signal was detected, but there is not enough historical evidence to support a reliable explanation.",

      outcomeTitle:
        "A business signal was detected, but the cause remains unconfirmed.",

      outcomeDescription:
        "The engine deliberately abstained from assigning a specific driver because the available historical evidence is insufficient.",

      hypothesisTitle:
        "No reliable hypothesis assigned",

      confidenceTitle:
        "The engine abstained because the available evidence is insufficient.",

      summaryStatus:
        "INVESTIGATION PAUSED",
    },
  };

  const currentScenarioContent =
    scenarioContent[scenario];

  const personaContent = {

    heroDescription: isExecutive
      ? "A high-priority business signal requires attention across revenue and inventory performance."
      : "A high-priority signal requires operational validation across inventory movement, replenishment activity and revenue behavior.",

    whyItMatters: isExecutive
      ? "Inventory is the dominant business signal and represents the primary operational risk requiring leadership attention."
      : "Inventory movement is statistically extreme relative to historical behavior and should be validated against movement and replenishment records.",

    actionTitle: isExecutive
      ? "Validate the inventory signal before making a business decision."
      : "Trace inventory depletion and replenishment activity.",

    actionDescription: isExecutive
      ? "Validate the operational evidence before attributing the revenue movement to inventory."
      : "Review inventory movements, replenishment timing, quantities and historical stock behavior for the affected period.",

    confidenceDescription: isExecutive
      ? "The evidence is strong enough to justify attention, but not strong enough to establish causation."
      : "The score reflects the strength of the available evidence and highlights which operational facts still require validation.",

    decisionStatus: isExecutive
      ? "Leadership review recommended"
      : "Operational validation recommended",

    decisionDescription: isExecutive
      ? "The evidence supports investigation while causation remains unconfirmed."
      : "Validate the inventory movement against operational records before escalating the finding.",

  };

  const {
    case: investigationCase,
    history,
    priority,
    key_metrics,
    signals,
    hypothesis,
    confidence,
    business_summary,
    evidence_sufficiency,
  } = investigation;

  const isAbstained =
    evidence_sufficiency?.status === "INSUFFICIENT";

  const chartData = Array.isArray(history)
    ? history.map((item) => {
        const monthLabel = new Date(item.month).toLocaleDateString(
          "en-US",
          {
            month: "short",
            year: "numeric",
          }
        );

        return {
          month: monthLabel,
          revenue: item.revenue_deviation_pct,
          inventory: item.stock_change_pct,
          isInvestigationMonth:
            item.month.slice(0, 7) ===
            investigationCase.month.slice(0, 7),
        };
      })
    : [];

  const inventoryMovement = Math.abs(
    key_metrics.inventory.stock_change_pct
  );

  const revenueMovement = Math.abs(
    key_metrics.revenue.deviation_pct
  );

  const maxMovement = Math.max(
    inventoryMovement,
    revenueMovement
  );

  return (
    <div className="app">

      {running && (
        <div className="investigation-loading">
          <div className="investigation-loading-card">

            <div className="loader" />

            <span className="eyebrow">
              INVESTIGATION ENGINE
            </span>

            <h2>
              Running investigation
            </h2>

            <p>
              Analyzing evidence and preparing an updated
              investigation result.
            </p>

          </div>
        </div>
      )}

      {error && investigation && (
        <div className="investigation-error">
          <div>
            <span className="eyebrow">
              INVESTIGATION ERROR
            </span>

            <p>{error}</p>
          </div>

          <button
            className="error-retry"
            onClick={runInvestigation}
          >
            Retry
          </button>
        </div>
      )}

      {/* HEADER */}
      <header className="topbar">
        <div>
          <div className="brand">
            <span className="brand-mark">K</span>

            <div className="brand-info">
              <span className="brand-name">
                KPI Intelligence Engine
              </span>

              <span className="brand-type">
                BUSINESS INVESTIGATION PLATFORM
              </span>
            </div>
          </div>

          <div className="subtitle">
            Evidence-driven business investigation
          </div>
        </div>

        <div className="header-actions">
          <div className="persona-switch">

            <span className="persona-label">
              VIEW AS
            </span>

            <div className="persona-options">

              <button
                className={
                  persona === "EXECUTIVE"
                    ? "persona-option active"
                    : "persona-option"
                }
                onClick={() => setPersona("EXECUTIVE")}
              >
                Executive
              </button>

              <button
                className={
                  persona === "OPERATIONS"
                    ? "persona-option active"
                    : "persona-option"
                }
                onClick={() => setPersona("OPERATIONS")}
              >
                Operations
              </button>

            </div>

          </div>
          
          <div className="scenario-selector">
            <div className="scenario-label">
              INVESTIGATION SCENARIO
            </div>

            <select
              value={scenario}
              onChange={(e) =>
                setScenario(
                  e.target.value as InvestigationScenario
                )
              }
            >
              <option value="priority">
                Priority Case
              </option>

              <option value="limited">
                Limited Evidence
              </option>

              <option value="insufficient">
                Insufficient Evidence
              </option>
            </select>
          </div>

          <button
            className="run-button"
            onClick={runInvestigation}
            disabled={running}
          >
            {running ? (
              <>
                <span className="button-spinner" />
                Running...
              </>
            ) : (
              <>
                <span className="refresh-icon">↻</span>
                Run Investigation
              </>
            )}
          </button>

          <div className="engine-status">
            <span className="status-dot" />
            Investigation Engine Online
          </div>

        </div>
      </header>


      {/* INVESTIGATION HERO */}
      <main>

        <section className="hero">

          <div className="hero-left">

            <span className="eyebrow">
              {currentScenarioContent.heroEyebrow}
            </span>

            <h1>
              {investigation.signals.dominant_signal === "INVENTORY" ? (
                <>
                  Inventory anomaly
                  <br />
                  detected
                </>
              ) : investigation.signals.dominant_signal === "REVENUE" ? (
                <>
                  Revenue anomaly
                  <br />
                  detected
                </>
              ) : (
                <>
                  Business anomaly
                  <br />
                  detected
                </>
              )}
            </h1>

            <p className="hero-description">
              {isAbstained
                ? currentScenarioContent.heroDescription
                : personaContent.heroDescription}
            </p>

            <div className="case-context">

              <span>{investigationCase.category}</span>

              <span className="separator">•</span>

              <span>{investigationCase.region}</span>

              <span className="separator">•</span>

              <span>{investigationCase.warehouse}</span>

              <span className="separator">•</span>

              <span>{investigationCase.month}</span>

            </div>

            <div className="investigation-context">

              <div className="investigation-context-item">
                <span>CASE</span>
                <strong>
                  {investigation.signals.dominant_signal === "INVENTORY"
                    ? "Inventory anomaly"
                    : investigation.signals.dominant_signal === "REVENUE"
                    ? "Revenue anomaly"
                    : "Business anomaly"}
                </strong>
              </div>

              <div className="investigation-context-item">
                <span>REGION</span>
                <strong>{investigationCase.region}</strong>
              </div>

              <div className="investigation-context-item">
                <span>CATEGORY</span>
                <strong>{investigationCase.category}</strong>
              </div>

              <div className="investigation-context-item">
                <span>WAREHOUSE</span>
                <strong>{investigationCase.warehouse}</strong>
              </div>

              <div className="investigation-context-item">
                <span>PERIOD</span>
                <strong>
                  {new Date(investigationCase.month).toLocaleDateString(
                    "en-US",
                    {
                      month: "long",
                      year: "numeric"
                    }
                  )}
                </strong>
              </div>

            </div>

          </div>


          <div className="hero-right">

            <div className="priority-card">

              <span className="card-label">
                PRIORITY
              </span>

              <strong>
                {priority.level}
              </strong>

              <span>
                Score {priority.score}
              </span>

            </div>

            <div className="confidence-card">

              <span className="card-label">
                CONFIDENCE
              </span>

              <strong>
                {Math.round(confidence.score * 100)}%
              </strong>

              <span>
                {confidence.level}
              </span>

            </div>

          </div>

        </section>


        {/* KPI CARDS */}

        <section className="metrics-grid">

          <div className="metric-card">

            <div className="metric-header">
              <span>Revenue</span>
              <span className="metric-tag">ACTUAL</span>
            </div>

            <div className="metric-value">
              ${key_metrics.revenue.actual.toLocaleString()}
            </div>

            <div className="metric-change negative">
              ↓ {Math.abs(key_metrics.revenue.deviation_pct)}%
              <span> vs expected</span>
            </div>

            <div className="metric-secondary">
              Expected ${key_metrics.revenue.expected.toLocaleString()}
            </div>

          </div>


          <div className="metric-card critical">

            <div className="metric-header">
              <span>Inventory</span>
              <span className="metric-tag">DOMINANT SIGNAL</span>
            </div>

            <div className="metric-value">
              {key_metrics.inventory.current_stock}
            </div>

            <div className="metric-change negative">
              ↓ {Math.abs(key_metrics.inventory.stock_change_pct)}%
            </div>

            <div className="metric-secondary">
              Z-score {key_metrics.inventory.z_score !== null
                ? key_metrics.inventory.z_score.toFixed(2)
                : "N/A"}
            </div>

          </div>


          <div className="metric-card">

            <div className="metric-header">
              <span>Reorder Level</span>
            </div>

            <div className="metric-value">
              {key_metrics.inventory.reorder_level}
            </div>

            <div className="metric-secondary">
              Current stock is{" "}
              {key_metrics.inventory.below_reorder
                ? "below"
                : "above"}{" "}
              reorder level
            </div>

          </div>

        </section>

        {/* EVIDENCE QUALITY */}

        <section className="evidence-quality">

          <div className="evidence-quality-header">

            <div>
              <span className="eyebrow">
                EVIDENCE QUALITY
              </span>

              <h2>
                How much evidence does the engine have?
              </h2>
            </div>

            <div
              className={`evidence-quality-status ${evidence_sufficiency.status.toLowerCase()}`}
            >
              {evidence_sufficiency.status}
            </div>

          </div>

          <div className="evidence-quality-grid">

            <div className="evidence-quality-item">

              <span>
                HISTORICAL BASELINE
              </span>

              <strong>
                {evidence_sufficiency.baseline_months}
              </strong>

              <p>
                historical observations available
              </p>

            </div>


            <div className="evidence-quality-item">

              <span>
                MINIMUM REQUIRED
              </span>

              <strong>
                {evidence_sufficiency.minimum_required}
              </strong>

              <p>
                observations required for investigation
              </p>

            </div>


            <div className="evidence-quality-item">

              <span>
                ENGINE DECISION
              </span>

              <strong>
                {evidence_sufficiency.status === "SUFFICIENT"
                  ? "INVESTIGATE"
                  : evidence_sufficiency.status === "LIMITED"
                  ? "CAUTIOUS"
                  : "ABSTAIN"}
              </strong>

              <p>
                {evidence_sufficiency.status === "SUFFICIENT"
                  ? "Normal investigation confidence"
                  : evidence_sufficiency.status === "LIMITED"
                  ? "Confidence is deliberately constrained"
                  : "No causal attribution is produced"}
              </p>

            </div>

          </div>

        </section>

        {isAbstained && (
          <div className="abstention-banner">
            <div className="abstention-icon">
              !
            </div>

            <div className="abstention-content">
              <div className="abstention-title">
                Investigation paused — insufficient evidence
              </div>

              <div className="abstention-message">
                The engine detected a business signal but deliberately
                avoided assigning a specific cause because the available
                historical evidence is insufficient.
              </div>

              <div className="abstention-meta">
                {evidence_sufficiency?.baseline_months ?? 0} historical
                observations available ·{" "}
                {evidence_sufficiency?.minimum_required ?? 2} required
              </div>
            </div>
          </div>
        )}

        {/* INVESTIGATION OUTCOME */}

        <section className="investigation-outcome">

          <div className="investigation-outcome-header">

            <div>
              <span className="eyebrow">
                INVESTIGATION OUTCOME
              </span>

              <h2>
                What is happening, why it matters, and what should happen next?
              </h2>
            </div>

          </div>


          <div className="outcome-grid">

            {/* WHAT HAPPENED */}

            <div className="outcome-block">

              <span className="outcome-label">
                01 · WHAT HAPPENED
              </span>

              <h3>
                {currentScenarioContent.outcomeTitle}
              </h3>

              <div className="outcome-metrics">

                <div>
                  <strong>
                    {key_metrics.revenue.deviation_pct.toFixed(2)}%
                  </strong>

                  <span>
                    Revenue deviation
                  </span>
                </div>

                <div>
                  <strong>
                    {key_metrics.inventory.stock_change_pct.toFixed(2)}%
                  </strong>

                  <span>
                    Inventory movement
                  </span>
                </div>

              </div>

              <p>
                {currentScenarioContent.outcomeDescription}
              </p>

            </div>


            {/* WHY IT MATTERS */}

            <div className="outcome-block">

              <span className="outcome-label">
                02 · WHY IT MATTERS
              </span>

              <h3>
                {isExecutive
                  ? "Inventory is the dominant business signal."
                  : "Inventory movement requires operational validation."}
              </h3>

              <p>
                {personaContent.whyItMatters}
              </p>

            </div>


            {/* WHAT TO DO */}

            <div className="outcome-block outcome-action">

              <span className="outcome-label">
                03 · WHAT TO DO
              </span>

              <h3>
                {personaContent.actionTitle}
              </h3>

              <p>
                {personaContent.actionDescription}
              </p>

            </div>

          </div>


          {/* CAUSALITY NOTE */}

          <div className="outcome-caveat">

            <span>IMPORTANT</span>

            <p>
              The evidence supports investigation of the inventory signal,
              but does not establish that inventory changes caused the
              revenue decline.
            </p>

          </div>

        </section>


        {/* INVESTIGATION FLOW */}

        {isAbstained ? (

        <section className="section abstention-section">

          <div className="section-heading">
            <div>
              <span className="eyebrow">
                INVESTIGATION DECISION
              </span>

              <h2>
                The engine stopped before attribution.
              </h2>
            </div>
          </div>


          <div className="abstention-detail-grid">

            <div className="abstention-detail-card">

              <span className="outcome-label">
                01 · WHY WE ABSTAINED
              </span>

              <h3>
                The available history is not sufficient.
              </h3>

              <p>
                The engine detected a business signal, but there
                are not enough historical observations to determine
                whether the change is genuinely unusual or identify
                a reliable underlying driver.
              </p>

            </div>


            <div className="abstention-detail-card">

              <span className="outcome-label">
                02 · WHAT IS MISSING
              </span>

              <div className="abstention-list">

                <div>
                  <span>01</span>
                  <p>
                    Additional historical observations
                  </p>
                </div>

                <div>
                  <span>02</span>
                  <p>
                    Relevant operational or business context
                  </p>
                </div>

                <div>
                  <span>03</span>
                  <p>
                    Evidence that can validate the suspected driver
                  </p>
                </div>

              </div>

            </div>


            <div className="abstention-detail-card">

              <span className="outcome-label">
                03 · NEXT STEP
              </span>

              <h3>
                Collect evidence and re-run the investigation.
              </h3>

              <p>
                No causal attribution is produced until the evidence
                threshold is met.
              </p>

            </div>

          </div>

        </section>

      ) : (

        <section className="section">

          <section className="section">

                <div className="section-heading">
                  <div>
                    <span className="eyebrow">
                      INVESTIGATION FLOW
                    </span>

                    <h2>
                      From signal to action
                    </h2>
                  </div>
                </div>


                <div className="investigation-flow">

                  <div className="flow-node">
                    <span>01</span>
                    <strong>Signal</strong>
                    <p>
                      {investigation.signals.revenue_declined &&
                      investigation.signals.inventory_declined
                        ? "Revenue and inventory declined"
                        : investigation.signals.inventory_declined
                        ? "Inventory declined"
                        : investigation.signals.revenue_declined
                        ? "Revenue declined"
                        : "No major decline detected"}
                    </p>
                  </div>

                  <div className="flow-line">
                    <div className="flow-line-pulse" />
                  </div>

                  <div className="flow-node">
                    <span>02</span>
                    <strong>Evidence</strong>
                    <p>
                      {investigation.key_metrics.inventory.status ===
                      "RAPID_STOCK_DECLINE"
                        ? "Inventory movement is statistically extreme"
                        : "Inventory movement requires review"}
                    </p>
                  </div>

                  <div className="flow-line">
                    <div className="flow-line-pulse" />
                  </div>

                  <div className="flow-node">
                    <span>03</span>
                    <strong>Hypothesis</strong>
                    <p>{investigation.hypothesis.statement}</p>
                  </div>

                  <div className="flow-line">
                    <div className="flow-line-pulse" />
                  </div>

                  <div className="flow-node">
                    <span>04</span>
                    <strong>Action</strong>
                    <p>{investigation.recommendation.action}</p>
                  </div>

                </div>

              </section>

        </section>

      )}



        {/* EVIDENCE + HYPOTHESIS */}

        {!isAbstained && (
          <section className="analysis-grid">

            <div className="panel">
              <div className="panel-header">
                <div>
                  <span className="eyebrow">
                    STATISTICAL EVIDENCE
                  </span>

                  <h2>Why this case matters</h2>
                </div>

                <span className="signal-badge">
                  {signals.dominant_signal}
                </span>
              </div>

              <div className="evidence-row">

                <div className="evidence-metric">

                  <div className="evidence-metric-header">
                    <span>Inventory movement</span>

                    <strong>
                      {key_metrics.inventory.stock_change_pct}%
                    </strong>
                  </div>

                  <div className="evidence-bar">
                    <div
                      className="evidence-bar-fill"
                      style={{
                        width: `${(inventoryMovement / maxMovement) * 100}%`
                      }}
                    />
                  </div>

                </div>

                <span className="extreme">
                  {key_metrics.inventory.status ===
                  "RAPID_STOCK_DECLINE"
                    ? "EXTREME"
                    : "REVIEW"}
                </span>

              </div>

              <div className="evidence-row">
                <div>
                  <span>Inventory z-score</span>
                  <strong>
                    {key_metrics.inventory.z_score !== null
                      ? key_metrics.inventory.z_score.toFixed(2)
                      : "N/A"}
                  </strong>
                </div>

                <span className="extreme">
                  STATISTICAL SIGNAL
                </span>
              </div>

              <div className="evidence-row">

                <div className="evidence-metric">

                  <div className="evidence-metric-header">
                    <span>Revenue deviation</span>

                    <strong>
                      {key_metrics.revenue.deviation_pct}%
                    </strong>
                  </div>

                  <div className="evidence-bar">
                    <div
                      className="evidence-bar-fill"
                      style={{
                        width: `${(revenueMovement / maxMovement) * 100}%`
                      }}
                    />
                  </div>

                </div>

                <span className="normal">
                  {key_metrics.revenue.z_score !== null &&
                  Math.abs(key_metrics.revenue.z_score) >= 2
                    ? "ANOMALOUS"
                    : "NORMAL"}
                </span>

              </div>

              <div className="timeline-chart">

                <div className="timeline-chart-header">
                  <div>
                    <span className="chart-label">
                      PERFORMANCE TRAJECTORY
                    </span>

                    <strong>
                      Historical signal movement
                    </strong>
                  </div>
                </div>

                <div
                  className="chart-container"
                  style={{
                    width: "100%",
                    height: "280px",
                    minHeight: "280px",
                  }}
                >

                  {chartData.length > 0 ? (
                    <ResponsiveContainer
                      width="100%"
                      height="100%"
                    >

                      <LineChart
                        data={chartData}
                        margin={{
                          top: 10,
                          right: 10,
                          left: -20,
                          bottom: 5,
                        }}
                      >
                        <CartesianGrid
                          strokeDasharray="3 5"
                          vertical={false}
                          stroke="#252936"
                        />

                        <XAxis
                          dataKey="month"
                          tick={{
                            fill: "#7f8798",
                            fontSize: 10,
                          }}
                          axisLine={false}
                          tickLine={false}
                        />

                        <YAxis
                          domain={[-70, 35]}
                          tick={{
                            fill: "#7f8798",
                            fontSize: 10,
                          }}
                          tickFormatter={(value) => `${value}%`}
                          axisLine={false}
                          tickLine={false}
                        />

                        <ReferenceLine
                          y={0}
                          stroke="#596170"
                          strokeDasharray="4 4"
                        />

                        <Tooltip
                          contentStyle={{
                            background: "#11141b",
                            border: "1px solid #2b3040",
                            borderRadius: "8px",
                            fontSize: "12px",
                          }}
                          labelStyle={{
                            color: "#ffffff",
                            marginBottom: "4px",
                          }}
                          formatter={(value, name) => [
                            `${Number(value).toFixed(2)}%`,
                            name === "revenue" ? "Revenue" : "Inventory",
                          ]}
                        />

                        <Legend
                          verticalAlign="top"
                          align="right"
                          iconType="circle"
                          wrapperStyle={{
                            fontSize: "11px",
                            paddingBottom: "12px",
                          }}
                          formatter={(value) =>
                            value === "revenue"
                              ? "Revenue"
                              : "Inventory"
                          }
                        />

                        <Line
                          type="monotone"
                          dataKey="revenue"
                          stroke="#f1f3f7"
                          strokeWidth={2}
                          dot={{
                            r: 3,
                            fill: "#f1f3f7",
                            strokeWidth: 0,
                          }}
                          activeDot={{
                            r: 5,
                          }}
                        />

                        <Line
                          type="monotone"
                          dataKey="inventory"
                          stroke="#737b8c"
                          strokeWidth={2}
                          dot={{
                            r: 3,
                            fill: "#737b8c",
                            strokeWidth: 0,
                          }}
                          activeDot={{
                            r: 5,
                          }}
                        />

                        {chartData
                          .filter((item) => item.isInvestigationMonth)
                          .map((item) => (
                            <ReferenceDot
                              key={`investigation-${item.month}`}
                              x={item.month}
                              y={item.inventory}
                              r={6}
                              fill="#ffffff"
                              stroke="#101219"
                              strokeWidth={2}
                            />
                          ))}

                        {chartData
                          .filter((item) => item.isInvestigationMonth)
                          .map((item) => (
                            <ReferenceLine
                              key={`investigation-line-${item.month}`}
                              x={item.month}
                              stroke="#596170"
                              strokeDasharray="4 4"
                              label={{
                                value: "INVESTIGATION MONTH",
                                position: "insideTop",
                                fill: "#9aa2b1",
                                fontSize: 9,
                                fontWeight: 600,
                              }}
                            />
                          ))}
                      </LineChart>

                    </ResponsiveContainer>
                  ) : (
                    <div className="chart-empty">
                      Historical data unavailable.
                    </div>
                  )}

                </div>

              </div>

              <div className="evidence-divider" />

              <div className="evidence-summary">

                <div className="summary-icon">
                  →
                </div>

                <div>
                  <span>Dominant business signal</span>

                  <strong>
                    {signals.dominant_signal}
                  </strong>

                  <p>
                    Both inventory and revenue declined during
                    the case period, with inventory showing the
                    strongest statistical movement.
                  </p>
                </div>

              </div>

            </div>


            <div className="panel hypothesis-panel">

              <div className="hypothesis-panel-header">
                <div>
                  <span className="eyebrow">
                    AI INVESTIGATION HYPOTHESIS
                  </span>

                  <h2>
                    {hypothesis.type}
                  </h2>
                </div>

                <span className="hypothesis-badge">
                  {isAbstained
                    ? "NO ATTRIBUTION"
                    : evidence_sufficiency.status === "LIMITED"
                    ? "LIMITED EVIDENCE"
                    : "EVIDENCE GROUNDED"}
                </span>
              </div>

              <blockquote>
                “{hypothesis.statement}”
              </blockquote>

              <div className="hypothesis-insights">

                <div className="hypothesis-insight">
                  <span className="insight-label">
                    WHAT WE OBSERVED
                  </span>

                  <div className="insight-values">

                    <div>
                      <strong>
                        {key_metrics.inventory.stock_change_pct}%
                      </strong>

                      <span>
                        Inventory movement
                      </span>
                    </div>

                    <div>
                      <strong>
                        {key_metrics.revenue.deviation_pct}%
                      </strong>

                      <span>
                        Revenue deviation
                      </span>
                    </div>

                    <div>
                      <strong>
                        {key_metrics.inventory.z_score !== null
                          ? key_metrics.inventory.z_score.toFixed(2)
                          : "N/A"}
                      </strong>

                      <span>
                        Inventory z-score
                      </span>
                    </div>

                  </div>
                </div>


                <div className="hypothesis-insight">

                  <span className="insight-label">
                    WHAT THIS SUGGESTS
                  </span>

                  <p>
                    The observed inventory decline is a plausible
                    signal associated with the revenue decline during
                    the investigation period.
                  </p>

                </div>


                <div className="hypothesis-insight">

                  <span className="insight-label">
                    WHAT REMAINS UNKNOWN
                  </span>

                  <p>
                    The available evidence does not establish whether
                    the inventory decline directly caused the revenue
                    decline.
                  </p>

                </div>

              </div>


              <div className="hypothesis-note">

                <span className="note-icon">
                  !
                </span>

                <p>
                  This is an evidence-grounded hypothesis.
                  The available evidence does not establish
                  causation.
                </p>

              </div>

            </div>

          </section>
        )}


        {/* CONFIDENCE */}

          {!isAbstained && (
          <section className="confidence-section">

            <div className="confidence-copy">

              <span className="eyebrow">
                CONFIDENCE ASSESSMENT
              </span>

              <h2>
                {currentScenarioContent.confidenceTitle}
              </h2>

              <p className="confidence-description">
                {personaContent.confidenceDescription}
              </p>

            </div>


            <div className="confidence-score">

              <div className="score">
                {Math.round(confidence.score * 100)}
                <span>%</span>
              </div>

              <div className="confidence-level">
                {confidence.level} CONFIDENCE
              </div>

              <div className="confidence-bar">
                <div
                  style={{
                    width: `${confidence.score * 100}%`,
                  }}
                />
              </div>

            </div>


            <div className="confidence-breakdown">

              {/* SUPPORTING */}

              <div className="confidence-factor supporting">

                <div className="factor-top">
                  <div>
                    <span>SUPPORTING EVIDENCE</span>
                    <strong>
                      +{confidence.supporting_score}
                    </strong>
                  </div>

                  <span className="factor-status">
                    STRENGTHENS
                  </span>
                </div>

                <p>
                  Signals that strengthen the investigation.
                </p>

                <div className="factor-list">

                  <div>
                    <span>01</span>
                    <p>Inventory decline detected</p>
                  </div>

                  <div>
                    <span>02</span>
                    <p>Revenue decline detected</p>
                  </div>

                  <div>
                    <span>03</span>
                    <p>Inventory is the dominant signal</p>
                  </div>

                  <div>
                    <span>04</span>
                    <p>Inventory movement is statistically extreme</p>
                  </div>

                </div>

              </div>


              {/* WEAKENING */}

              <div className="confidence-factor weakening">

                <div className="factor-top">
                  <div>
                    <span>WEAKENING EVIDENCE</span>
                    <strong>
                      −{confidence.weakening_score}
                    </strong>
                  </div>

                  <span className="factor-status">
                    LIMITS CERTAINTY
                  </span>
                </div>

                <p>
                  Factors that limit certainty or prevent
                  a causal conclusion.
                </p>

                <div className="factor-list">

                  <div>
                    <span>01</span>
                    <p>Causation has not been established</p>
                  </div>

                </div>

              </div>

            </div>


            <div className="confidence-explanation">

              <div className="explanation-icon">
                ✓
              </div>

              <div>
                <span>HOW TO READ THIS SCORE</span>

                <p>
                  High confidence means the available evidence strongly
                  supports investigating this case. It does not mean the
                  underlying cause has been confirmed.
                </p>
              </div>

            </div>

          </section>
          )}


        {/* RECOMMENDATION */}

        {!isAbstained && (
          <section className="recommendation-section">

            <div className="recommendation-header">

              <div>
                <span className="eyebrow">
                  RECOMMENDED ACTION
                </span>

                <h2>
                  {isExecutive
                    ? "Validate the inventory signal"
                    : "Trace the inventory movement"}
                </h2>

                <p className="recommendation-lead">
                  {isExecutive
                    ? "Before attributing revenue impact to inventory changes, validate the operational evidence behind the signal."
                    : "Review the inventory trail and replenishment activity before escalating the finding."}
                </p>
              </div>

              <div className="urgency-badge">
                {investigation.recommendation.urgency}
              </div>

            </div>

            <div className="recommendation-body">

              <div className="recommendation-reason">

                <span className="eyebrow">
                  WHY THIS ACTION
                </span>

                <div className="reason-list">

                  {investigation.recommendation.reason.map(
                    (reason, index) => (
                      <div
                        className="reason-item"
                        key={index}
                      >
                        <span className="reason-number">
                          {String(index + 1).padStart(2, "0")}
                        </span>

                        <p>{reason}</p>
                      </div>
                    )
                  )}

                </div>

              </div>


              <div className="recommendation-next">

                <span className="eyebrow">
                  NEXT STEPS
                </span>

                <div className="next-step-list">

                  <div className="next-step">
                    <span>01</span>
                    <p>Review inventory movement records.</p>
                  </div>

                  <div className="next-step">
                    <span>02</span>
                    <p>
                      Compare replenishment timing and quantities
                      against expected patterns.
                    </p>
                  </div>

                  <div className="next-step">
                    <span>03</span>
                    <p>
                      Check whether the observed stock reduction
                      was operationally expected.
                    </p>
                  </div>

                </div>

              </div>

            </div>


            <div className="decision-status">

              <span className="decision-dot" />

              <div>
                <strong>
                  {personaContent.decisionStatus}
                </strong>

                <p>
                  {personaContent.decisionDescription}
                </p>
              </div>

            </div>


            {investigation.recommendation.causal_warning && (
              <div className="causal-warning">

                <span>CAUTION</span>

                <p>
                  {investigation.recommendation.causal_warning}
                </p>

              </div>
            )}

          </section>
        )}

        {/* EXECUTIVE BUSINESS SUMMARY */}

      <section className="executive-summary">

        <div className="executive-summary-header">

          <div>
            <span className="eyebrow">
              EXECUTIVE BUSINESS SUMMARY
            </span>

            <h2>
              {isExecutive
                ? "What leadership should know"
                : "What the investigation found"}
            </h2>

            <p>
              {isExecutive
                ? "A decision-oriented interpretation of the evidence, risk and recommended action."
                : "A diagnostic interpretation of the evidence, hypothesis and operational next steps."}
            </p>
          </div>

          <div className="summary-status">
            <span>
              {currentScenarioContent.summaryStatus}
            </span>
          </div>

        </div>

        <div className="summary-content">

          {/* 01 — EXECUTIVE SUMMARY */}
          <div className="summary-section">
            <span className="summary-index">01</span>

            <div>
              <span className="eyebrow">
                EXECUTIVE SUMMARY
              </span>

              <p>
                {getSummarySection(business_summary, 1)}
              </p>
            </div>
          </div>


          {/* 02 — KEY EVIDENCE */}
          <div className="summary-section">
            <span className="summary-index">02</span>

            <div>
              <span className="eyebrow">
                KEY EVIDENCE
              </span>

              <ul className="summary-evidence-list">

                <li>
                  <span>Inventory</span>
                  <strong>
                    {key_metrics.inventory.stock_change_pct.toFixed(2)}%
                  </strong>
                  <small>
                    Stock change
                  </small>
                </li>

                <li>
                  <span>Inventory deviation</span>
                  <strong>
                    {key_metrics.inventory.z_score !== null
                      ? key_metrics.inventory.z_score.toFixed(2)
                      : "N/A"}
                  </strong>
                  <small>
                    Z-score · {key_metrics.inventory.status}
                  </small>
                </li>

                <li>
                  <span>Revenue</span>
                  <strong>
                    {key_metrics.revenue.deviation_pct.toFixed(2)}%
                  </strong>
                  <small>
                    Deviation from expected
                  </small>
                </li>

                <li>
                  <span>Current stock</span>
                  <strong>
                    {key_metrics.inventory.current_stock}
                  </strong>
                  <small>
                    Reorder level: {key_metrics.inventory.reorder_level}
                  </small>
                </li>

              </ul>
            </div>
          </div>


          {/* 03 — INVESTIGATION HYPOTHESIS */}
          <div className="summary-section">
            <span className="summary-index">03</span>

            <div>
              <span className="eyebrow">
                INVESTIGATION HYPOTHESIS
              </span>

              <p>
                {getSummarySection(business_summary, 3)}
              </p>
            </div>
          </div>


          {/* 04 — RECOMMENDED ACTION */}
          <div className="summary-section summary-action">
            <span className="summary-index">04</span>

            <div>
              <span className="eyebrow">
                RECOMMENDED ACTION
              </span>

              <p className="summary-action-title">
                Validate the inventory signal
              </p>

              <div className="summary-next-steps">

                <div className="summary-step">
                  <span>01</span>
                  <p>Review inventory movement records.</p>
                </div>

                <div className="summary-step">
                  <span>02</span>
                  <p>
                    Compare replenishment timing and quantities
                    against expected patterns.
                  </p>
                </div>

                <div className="summary-step">
                  <span>03</span>
                  <p>
                    Check whether the observed stock reduction
                    was operationally expected.
                  </p>
                </div>

              </div>
            </div>
          </div>


          {/* 05 — IMPORTANT CAVEAT */}
          <div className="summary-section summary-caveat">
            <span className="summary-index">05</span>

            <div>
              <span className="eyebrow">
                IMPORTANT CAVEAT
              </span>

              <p>
                {getSummarySection(business_summary, 6)}
              </p>
            </div>
          </div>

        </div>

      </section>

      </main>

    </div>
  );
}

export default App;