import { useEffect, useRef, useState } from "react";
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

type Investigation = {
  case: {
    month: string;
    region: string;
    category: string;
    warehouse: string;
  };

  history: {
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
  }[];

  priority: {
    score: number;
    level: string;
  };

  key_metrics: {
    revenue: {
      actual: number;
      expected: number;
      deviation_pct: number;
      z_score: number;
    };

    inventory: {
      current_stock: number;
      reorder_level: number;
      stock_change_pct: number;
      z_score: number;
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
  const [investigation, setInvestigation] =
    useState<Investigation | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [running, setRunning] =
    useState(false);

  const initialRunRef = useRef(false);

  const runInvestigation = async () => {
    try {
      setRunning(true);
      setError("");

      const response = await fetch(
        "http://127.0.0.1:8001/investigation"
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
    if (initialRunRef.current) {
      return;
    }

    initialRunRef.current = true;

    runInvestigation();
  }, []);

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

  const {
    case: investigationCase,
    history,
    priority,
    key_metrics,
    signals,
    hypothesis,
    confidence,
    recommendation,
    business_summary,
  } = investigation;

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

            <div className="eyebrow">
              INVESTIGATION REQUIRED
            </div>

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
              A high-priority business signal requires investigation
              across revenue and inventory performance.
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
              Z-score {key_metrics.inventory.z_score.toFixed(2)}
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


        {/* INVESTIGATION FLOW */}

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


        {/* EVIDENCE + HYPOTHESIS */}

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
                  {key_metrics.inventory.z_score.toFixed(2)}
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
                {Math.abs(key_metrics.revenue.z_score) >= 2
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
                EVIDENCE GROUNDED
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
                      {key_metrics.inventory.z_score.toFixed(2)}
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


        {/* CONFIDENCE */}

          <section className="confidence-section">

            <div className="confidence-copy">

              <span className="eyebrow">
                CONFIDENCE ASSESSMENT
              </span>

              <h2>
                Evidence supports the investigation,
                but uncertainty remains.
              </h2>

              <p className="confidence-description">
                The confidence score reflects the balance between
                evidence supporting the hypothesis and factors that
                weaken the investigation.
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


        {/* RECOMMENDATION */}

        <section className="recommendation-section">

          <div className="recommendation-header">

            <div>
              <span className="eyebrow">
                RECOMMENDED ACTION
              </span>

              <h2>
                What should happen next?
              </h2>

              <p className="recommendation-lead">
                {investigation.recommendation.action}
              </p>
            </div>

            <div className="urgency-badge">
              {investigation.recommendation.urgency}
            </div>

          </div>


          <div className="recommendation-context">

            <div className="context-item">
              <span>PRIORITY</span>

              <strong>
                {investigation.recommendation.priority}
              </strong>

              <small>
                Score {investigation.recommendation.priority_score}
              </small>
            </div>


            <div className="context-item">
              <span>CONFIDENCE</span>

              <strong>
                {Math.round(
                  investigation.recommendation.confidence.score * 100
                )}%
              </strong>

              <small>
                {investigation.recommendation.confidence.level}
              </small>
            </div>


            <div className="context-item">
              <span>SIGNAL STRENGTH</span>

              <strong>
                {investigation.recommendation.signal_strength}
              </strong>

              <small>
                Investigation strength
              </small>
            </div>


            <div className="context-item">
              <span>DOMINANT SIGNAL</span>

              <strong>
                {investigation.signals.dominant_signal}
              </strong>

              <small>
                Primary investigation focus
              </small>
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

                {investigation.recommendation.next_steps.map(
                  (step, index) => (
                    <div
                      className="next-step"
                      key={index}
                    >
                      <span>
                        {String(index + 1).padStart(2, "0")}
                      </span>

                      <p>{step}</p>
                    </div>
                  )
                )}

              </div>

            </div>

          </div>


          <div className="decision-status">

            <span className="decision-dot" />

            <div>
              <strong>
                Investigation ready for action
              </strong>

              <p>
                The available evidence supports operational
                review, while causation remains unconfirmed.
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

        {/* EXECUTIVE BUSINESS SUMMARY */}

      <section className="executive-summary">

        <div className="executive-summary-header">

          <div>
            <span className="eyebrow">
              EXECUTIVE BUSINESS SUMMARY
            </span>

            <h2>
              What the investigation tells us
            </h2>

            <p>
              A concise business interpretation of the
              evidence, hypothesis, confidence and recommended action.
            </p>
          </div>

          <div className="summary-status">
            <span>INVESTIGATION COMPLETE</span>
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
                    {key_metrics.inventory.z_score.toFixed(2)}
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


          {/* 04 — CONFIDENCE */}
          <div className="summary-section">
            <span className="summary-index">04</span>

            <div>
              <span className="eyebrow">
                CONFIDENCE
              </span>

              <div className="summary-confidence">

                <div className="confidence-score">
                  <strong>
                    {Math.round(confidence.score * 100)}%
                  </strong>

                  <span>
                    {confidence.level}
                  </span>
                </div>

                <div className="confidence-details">
                  <div>
                    <span>SUPPORTING</span>
                    <strong>
                      {confidence.supporting_score}
                    </strong>
                  </div>

                  <div>
                    <span>WEAKENING</span>
                    <strong>
                      {confidence.weakening_score}
                    </strong>
                  </div>
                </div>

              </div>
            </div>
          </div>


          {/* 05 — RECOMMENDED ACTION */}
          <div className="summary-section summary-action">
            <span className="summary-index">05</span>

            <div>
              <span className="eyebrow">
                RECOMMENDED ACTION
              </span>

              <p className="summary-action-title">
                {recommendation.action}
              </p>

              <div className="summary-next-steps">

                {recommendation.next_steps.map(
                  (step: string, index: number) => (
                    <div
                      className="summary-step"
                      key={index}
                    >
                      <span>
                        {String(index + 1).padStart(2, "0")}
                      </span>

                      <p>{step}</p>
                    </div>
                  )
                )}

              </div>
            </div>
          </div>


          {/* 06 — IMPORTANT CAVEAT */}
          <div className="summary-section summary-caveat">
            <span className="summary-index">06</span>

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