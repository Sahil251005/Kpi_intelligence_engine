import time
import pandas as pd
from Backend.analytics import (
    get_top_investigation_case,
    get_case_history,
    analyze_case_history,
    calculate_z_scores,
    assess_evidence_sufficiency,
    build_hybrid_assessment,
    build_evidence,
    calculate_hypothesis_confidence,
    calculate_driver_decomposition,
)

from Backend.llm import (
    generate_hypotheses,
    generate_business_summary,
)

from Backend.nlp import analyze_hypothesis_language

from Backend.recommendation import generate_recommendation


def run_investigation(scenario="priority"):

    investigation_start = time.perf_counter()

    print("DEBUG RUN INVESTIGATION SCENARIO:", scenario)

    if scenario == "insufficient":
        top_case = {
            "month": pd.Timestamp("2018-10-01"),
            "region": "TEST",
            "product_category_name": "abstention_test",
            "warehouse_location": "TEST-Warehouse",
            "revenue": 10000,
            "expected_revenue": 15000,
            "revenue_deviation_pct": -33.33,
            "current_stock": 100,
            "reorder_level": 200,
            "stock_change_pct": -50.00,
            "inventory_status": "CRITICAL",
            "below_reorder": True,
            "business_signal": "TEST_ABSTENTION",
            "priority_score": 999,
            "priority_level": "HIGH",
            "revenue_score": 3,
            "inventory_score": 6,
            "reorder_score": 0,
        }

        history = pd.DataFrame([
            {
                "month": pd.Timestamp("2018-10-01"),
                "region": "TEST",
                "product_category_name": "abstention_test",
                "revenue": 10000,
                "expected_revenue": 15000,
                "revenue_deviation_pct": -33.33,
                "current_stock": 100,
                "reorder_level": 200,
                "stock_change_pct": -50.00,
                "inventory_status": "CRITICAL",
                "business_signal": "TEST_ABSTENTION",
                "priority_score": 999,
                "priority_level": "HIGH",
            }
        ])

    elif scenario == "sparse":

        # --------------------------------------------------
        # Real sparse-history test case
        #
        # Target: AC / esporte_lazer / July 2018
        #
        # The target comes from the revenue analytics view.
        # The category has sparse own history, so the engine
        # should use peer-category history as contextual benchmark evidence.
        # --------------------------------------------------

        from Backend.database import get_engine

        engine = get_engine()

        # --------------------------------------------------
        # 1. Load target observation
        # --------------------------------------------------

        target_query = """
            SELECT
                month,
                region,
                product_category_name,
                revenue,
                total_orders,
                items_sold
            FROM analytics_revenue_region_category
            WHERE region = 'AC'
            AND product_category_name = 'esporte_lazer'
            AND month = '2018-07-01';
        """

        target_df = pd.read_sql(
            target_query,
            engine
        )

        if target_df.empty:
            return None

        target = target_df.iloc[0]

        # --------------------------------------------------
        # 2. Load own category history
        # --------------------------------------------------

        own_history_query = """
            SELECT
                month,
                region,
                product_category_name,
                revenue,
                total_orders,
                items_sold
            FROM analytics_revenue_region_category
            WHERE region = %(region)s
            AND product_category_name = %(category)s
            AND month < %(target_month)s
            ORDER BY month;
        """

        own_history = pd.read_sql(
            own_history_query,
            engine,
            params={
                "region": "AC",
                "category": "esporte_lazer",
                "target_month": target["month"]
            }
        )

        # --------------------------------------------------
        # 3. Build minimal investigation history
        #
        # The evidence gate only needs the historical
        # observation count. The real revenue values remain
        # available for driver decomposition.
        # --------------------------------------------------

        history = own_history.copy()

        if history.empty:
            history = pd.DataFrame(
                columns=[
                    "month",
                    "region",
                    "product_category_name",
                    "revenue",
                    "expected_revenue",
                    "revenue_deviation_pct",
                    "current_stock",
                    "reorder_level",
                    "stock_change_pct",
                    "inventory_status",
                    "business_signal",
                    "priority_score",
                    "priority_level",
                    "revenue_score",
                    "inventory_score",
                    "reorder_score"
                ]
            )
        else:
            history["expected_revenue"] = history["revenue"]
            history["revenue_deviation_pct"] = 0.0
            history["current_stock"] = 0
            history["reorder_level"] = 0
            history["stock_change_pct"] = 0.0
            history["inventory_status"] = "UNKNOWN"
            history["business_signal"] = "SPARSE_HISTORY_TEST"
            history["priority_score"] = 1
            history["priority_level"] = "MEDIUM"
            history["revenue_score"] = 0
            history["inventory_score"] = 0
            history["reorder_score"] = 0

        # --------------------------------------------------
        # 4. Create target case
        # --------------------------------------------------

        top_case = {
            "month": target["month"],
            "region": target["region"],
            "product_category_name":
                target["product_category_name"],

            "warehouse_location":
                "AC-Sparse-Test",

            "revenue":
                float(target["revenue"]),

            "expected_revenue":
                float(target["revenue"]),

            "revenue_deviation_pct":
                0.0,

            "current_stock":
                0,

            "reorder_level":
                0,

            "stock_change_pct":
                0.0,

            "inventory_status":
                "UNKNOWN",

            "below_reorder":
                False,

            "business_signal":
                "SPARSE_HISTORY_TEST",

            "priority_score":
                1,

            "priority_level":
                "MEDIUM",

            "revenue_score":
                0,

            "inventory_score":
                0,

            "reorder_score":
                0,
        }

        # Add target to history so downstream functions
        # can see the investigation period.
        target_history = pd.DataFrame([{
            "month": target["month"],
            "region": target["region"],
            "product_category_name":
                target["product_category_name"],
            "revenue":
                float(target["revenue"]),
            "expected_revenue":
                float(target["revenue"]),
            "revenue_deviation_pct":
                0.0,
            "current_stock":
                0,
            "reorder_level":
                0,
            "stock_change_pct":
                0.0,
            "inventory_status":
                "UNKNOWN",
            "business_signal":
                "SPARSE_HISTORY_TEST",
            "priority_score":
                1,
            "priority_level":
                "MEDIUM",
            "revenue_score":
                0,
            "inventory_score":
                0,
            "reorder_score":
                0,
        }])

        history = pd.concat(
            [history, target_history],
            ignore_index=True
        )

        history = history.sort_values(
            "month"
    ).reset_index(drop=True)

    elif scenario == "limited":
        top_case = {
            "month": pd.Timestamp("2018-10-01"),
            "region": "TEST",
            "product_category_name": "limited_evidence_test",
            "warehouse_location": "TEST-Warehouse",
            "revenue": 12000,
            "expected_revenue": 15000,
            "revenue_deviation_pct": -20.00,
            "current_stock": 150,
            "reorder_level": 200,
            "stock_change_pct": -25.00,
            "inventory_status": "LOW",
            "below_reorder": True,
            "business_signal": "TEST_LIMITED_EVIDENCE",
            "priority_score": 900,
            "priority_level": "HIGH",
            "revenue_score": 4,
            "inventory_score": 6,
            "reorder_score": 1,
        }

        history = pd.DataFrame([
            {
                "month": pd.Timestamp("2018-08-01"),
                "region": "TEST",
                "product_category_name": "limited_evidence_test",
                "revenue": 14000,
                "expected_revenue": 14500,
                "revenue_deviation_pct": -3.45,
                "current_stock": 220,
                "reorder_level": 200,
                "stock_change_pct": 5.00,
                "inventory_status": "HEALTHY",
                "business_signal": "NORMAL",
                "priority_score": 100,
                "priority_level": "LOW",
            },
            {
                "month": pd.Timestamp("2018-09-01"),
                "region": "TEST",
                "product_category_name": "limited_evidence_test",
                "revenue": 13500,
                "expected_revenue": 14500,
                "revenue_deviation_pct": -6.90,
                "current_stock": 200,
                "reorder_level": 200,
                "stock_change_pct": -9.09,
                "inventory_status": "HEALTHY",
                "business_signal": "NORMAL",
                "priority_score": 120,
                "priority_level": "LOW",
            },
            {
                "month": pd.Timestamp("2018-10-01"),
                "region": "TEST",
                "product_category_name": "limited_evidence_test",
                "revenue": 12000,
                "expected_revenue": 15000,
                "revenue_deviation_pct": -20.00,
                "current_stock": 150,
                "reorder_level": 200,
                "stock_change_pct": -25.00,
                "inventory_status": "LOW",
                "business_signal": "TEST_LIMITED_EVIDENCE",
                "priority_score": 900,
                "priority_level": "HIGH",
            }
        ])

    else:
        top_case = get_top_investigation_case()

        if top_case is None:
            return None

        history = get_case_history(
            top_case["region"],
            top_case["product_category_name"]
        )

    # --------------------------------------------------
    # 2A. Evidence sufficiency
    # --------------------------------------------------

    peer_months = 0

    if (
        top_case["region"] != "TEST"
        and top_case["product_category_name"]
    ):
        from Backend.database import get_engine

        engine = get_engine()

        peer_query = """
            SELECT DISTINCT month
            FROM analytics_revenue_region_category
            WHERE region = %(region)s
            AND product_category_name <> %(category)s
            AND month < %(target_month)s
            ORDER BY month;
        """

        peer_df = pd.read_sql(
            peer_query,
            engine,
            params={
                "region": top_case["region"],
                "category": top_case["product_category_name"],
                "target_month": top_case["month"]
            }
        )

        peer_months = len(peer_df)

    evidence_sufficiency = assess_evidence_sufficiency(
        history,
        top_case["month"],
        peer_months
    )

    print("DEBUG SPARSE HISTORY MONTHS:",
        len(history[history["month"] < top_case["month"]]))

    print("DEBUG PEER MONTHS:",
        peer_months)

    print("DEBUG EVIDENCE SUFFICIENCY:",
        evidence_sufficiency)

    # --------------------------------------------------
    # 2A-B. Sparse-history peer fallback
    # --------------------------------------------------

    if (
        evidence_sufficiency["baseline_source"] == "PEER_HISTORY"
        and scenario == "sparse"
    ):

        driver_decomposition = calculate_driver_decomposition(
            region=top_case["region"],
            product_category_name=top_case["product_category_name"],
            target_month=top_case["month"],
            inventory_history=history
        )

        total_runtime_ms = (
            time.perf_counter() - investigation_start
        ) * 1000

        return {
            "case": top_case,

            "history": history.to_dict(
                orient="records"
            ),

            "analysis": None,

            "z_scores": None,

            "hybrid": None,

            "driver_decomposition":
                driver_decomposition,

            "evidence_lineage": [
                {
                    "source": "Olist PostgreSQL dataset",
                    "dataset": "analytics_revenue_region_category",
                    "method": "SQL aggregation by region, category and month",
                    "freshness": str(top_case["month"]),
                    "contribution": "PRIMARY",
                    "confidence": None,
                },
                {
                    "source": "Peer-category history",
                    "dataset": "analytics_revenue_region_category",
                    "method": "Peer-category historical benchmark",
                    "freshness": str(top_case["month"]),
                    "contribution": "SUPPORTING",
                    "confidence": None,
                }
            ],

            "evidence": {
                "status": "LIMITED",
                "available_evidence": {
                    "own_baseline_months":
                        evidence_sufficiency["baseline_months"],
                    "peer_baseline_months":
                        peer_months,
                    "baseline_source":
                        "PEER_HISTORY"
                },
                "reasons":
                    evidence_sufficiency["reasons"]
            },

            "evidence_sufficiency":
                evidence_sufficiency,

            "hypotheses": [],

            "nlp": [],

            "selected_hypothesis": {
                "type": "LIMITED_EVIDENCE",
                "statement":
                    "The category has sparse own history. "
                    "Peer-category history is available as contextual "
                    "benchmark evidence, but the evidence is "
                    "insufficient for a reliable category-specific attribution."
            },

            "confidence": {
                "confidence_score": 0,
                "confidence_level": "LOW",
                "supporting_score": 0,
                "weakening_score": 0,
                "evidence_breakdown": [
                    (
                        "Sparse own category history",
                        -1
                    ),
                    (
                        "Peer history available as contextual benchmark",
                        0
                    )
                ]
            },

            "recommendation": {
                "action":
                    "Use the peer benchmark for contextual monitoring "
                    "and collect additional category-specific history "
                    "before assigning a driver.",

                "urgency": "MONITOR",

                "priority":
                    top_case["priority_level"],

                "priority_score":
                    top_case["priority_score"],

                "confidence": {
                    "score": 0,
                    "level": "LOW"
                },

                "reason": [
                    "Own category history contains fewer than "
                    "2 historical observations.",
                    "Peer-category history is available but does "
                    "not establish category-specific causation."
                ],

                "weakening_factors":
                    evidence_sufficiency["reasons"],

                "next_steps": [
                    "Collect additional category-level history.",
                    "Compare the category against peer-category trends.",
                    "Re-run the investigation when sufficient history is available."
                ],

                "confidence_note":
                    "Peer history is being used only as contextual "
                    "benchmark evidence; category-specific attribution "
                    "is intentionally constrained.",

                "causal_warning":
                    "Peer similarity does not establish causation.",

                "signal_strength": 0
            },

            "business_summary":
                "The engine detected a sparse-history case with only "
                f"{evidence_sufficiency['baseline_months']} own historical "
                f"observation(s), while {peer_months} peer-category months "
                "are available. Peer history is therefore used as a contextual "
                "benchmark evidence, but the engine does not assign a "
                "specific causal driver.",

            "runtime_telemetry": {
                "total_runtime_ms":
                    round(total_runtime_ms, 2),

                "analytics_runtime_ms":
                    round(total_runtime_ms, 2),

                "hypothesis_llm_runtime_ms": 0,

                "summary_llm_runtime_ms": 0,

                "llm_runtime_ms": 0,

                "llm_used": False,

                "decision_path":
                    "Evidence → Peer Fallback → Constrained Attribution",

                "evidence_sources": 2
            }
        }
    

    # --------------------------------------------------
    # 2B. Evidence sufficiency gate
    # --------------------------------------------------

    if evidence_sufficiency["status"] == "INSUFFICIENT":

        reasons = evidence_sufficiency.get(
            "reasons",
            []
        )

        total_runtime_ms = (
            time.perf_counter() - investigation_start
        ) * 1000

        return {
            "case": top_case,

            "history": history.to_dict(
                orient="records"
            ),

            "analysis": None,

            "z_scores": None,

            "hybrid": None,

            "evidence": {
                "status": "INSUFFICIENT",
                "available_evidence": {
                    "baseline_months":
                        evidence_sufficiency[
                            "baseline_months"
                        ]
                },
                "reasons": reasons
            },

            "evidence_sufficiency":
                evidence_sufficiency,

            "hypotheses": [],

            "nlp": [],

            "selected_hypothesis": {
                "type": "INSUFFICIENT_EVIDENCE",
                "statement":
                    "The available evidence is insufficient "
                    "to identify a reliable underlying driver."
            },

            "confidence": {
                "confidence_score": 0,
                "confidence_level": "INSUFFICIENT",
                "supporting_score": 0,
                "weakening_score": 0,
                "evidence_breakdown": []
            },

            "recommendation": {
                "action":
                    "Do not attribute the KPI change "
                    "to a specific cause yet.",

                "urgency": "MONITOR",

                "priority":
                    top_case["priority_level"],

                "priority_score":
                    top_case["priority_score"],

                "confidence": {
                    "score": 0,
                    "level": "INSUFFICIENT"
                },

                "reason": [
                    "Historical evidence is insufficient "
                    "for reliable causal interpretation."
                ],

                "weakening_factors": reasons,

                "next_steps": [
                    "Collect additional historical observations.",
                    "Add relevant operational or business context.",
                    "Re-run the investigation when additional evidence is available."
                ],

                "confidence_note":
                    "The engine abstained because "
                    "the available evidence is insufficient.",

                "causal_warning":
                    "No causal conclusion should be drawn "
                    "from the current evidence.",

                "signal_strength": 0
            },

            "business_summary":
                "The investigation identified a business signal, "
                "but there is insufficient historical evidence "
                "to determine whether the observed change is "
                "unusual or to support a specific underlying explanation.",

            "runtime_telemetry": {
                "total_runtime_ms": round(
                    total_runtime_ms,
                    2
                ),

                "analytics_runtime_ms": round(
                    total_runtime_ms,
                    2
                ),

                "hypothesis_llm_runtime_ms": 0,

                "summary_llm_runtime_ms": 0,

                "llm_runtime_ms": 0,

                "llm_used": False,

                "decision_path":
                    "Evidence → Abstention",

                "evidence_sources":
                    0
            },
        }

    # --------------------------------------------------
    # 3. Historical analysis
    # --------------------------------------------------

    analysis = analyze_case_history(
        history,
        top_case["month"]
    )

    # --------------------------------------------------
    # 4. Statistical anomaly analysis
    # --------------------------------------------------

    z_scores = calculate_z_scores(
        history,
        top_case["month"]
    )   

    # --------------------------------------------------
    # 4C. Driver decomposition
    # --------------------------------------------------

    driver_decomposition = calculate_driver_decomposition(
        region=top_case["region"],
        product_category_name=top_case["product_category_name"],
        target_month=top_case["month"],
        inventory_history=history
    )

    # --------------------------------------------------
    # 4D. Evidence lineage
    # --------------------------------------------------

    evidence_lineage = [
        {
            "source": "Olist PostgreSQL dataset",
            "dataset": "orders + order_items + products + customers",
            "method": "SQL aggregation by month, region and category",
            "freshness": str(top_case["month"]),
            "contribution": "PRIMARY",
            "confidence": None,
        },
        {
            "source": "Historical KPI baseline",
            "dataset": "Revenue and inventory history",
            "method": "Baseline comparison + z-score analysis",
            "freshness": str(top_case["month"]),
            "contribution": "PRIMARY",
            "confidence": None,
        },
        {
            "source": "Inventory context",
            "dataset": "inventory_context",
            "method": "Operational signal comparison",
            "freshness": str(top_case["month"]),
            "contribution": "SUPPORTING",
            "confidence": None,
        },

        # NEW
        {
            "source": "Customer reviews",
            "dataset": "reviews + orders + customers + products",
            "method": "Review score aggregation + sampled comment analysis",
            "freshness": str(top_case["month"]),
            "contribution": "SUPPORTING",
            "confidence": None,
        },

        {
            "source": "LLM investigation layer",
            "dataset": "Structured evidence generated by analytics pipeline",
            "method": "Hypothesis interpretation + business narrative",
            "freshness": "Generated at investigation time",
            "contribution": "INTERPRETATION",
            "confidence": None,
        },
    ]

    # --------------------------------------------------
    # 5. Hybrid assessment
    # --------------------------------------------------

    hybrid = build_hybrid_assessment(
        top_case,
        z_scores
    )

    # --------------------------------------------------
    # 6. Evidence
    # --------------------------------------------------

    evidence = build_evidence(
        top_case,
        analysis,
        z_scores,
        hybrid
    )

    # --------------------------------------------------
    # 6A. Customer feedback evidence
    # --------------------------------------------------

    from Backend.database import get_engine

    engine = get_engine()

    review_query = """
        SELECT
            r.review_score,
            r.review_comment_title,
            r.review_comment_message,
            r.review_creation_date
        FROM reviews r
        JOIN orders o
            ON r.order_id = o.order_id
        JOIN customers c
            ON o.customer_id = c.customer_id
        JOIN order_items oi
            ON o.order_id = oi.order_id
        JOIN products p
            ON oi.product_id = p.product_id
        WHERE c.customer_state = %(region)s
        AND p.product_category_name = %(category)s
        AND DATE_TRUNC(
                'month',
                o.order_purchase_timestamp
            ) = %(target_month)s
        ORDER BY r.review_creation_date DESC
        LIMIT 50;
    """

    review_df = pd.read_sql(
        review_query,
        engine,
        params={
            "region": top_case["region"],
            "category": top_case["product_category_name"],
            "target_month": top_case["month"]
        }
    )

    if not review_df.empty:

        review_scores = pd.to_numeric(
            review_df["review_score"],
            errors="coerce"
        ).dropna()

        comments = []

        for _, row in review_df.iterrows():

            title = (
                str(row["review_comment_title"])
                if pd.notna(row["review_comment_title"])
                else ""
            )

            message = (
                str(row["review_comment_message"])
                if pd.notna(row["review_comment_message"])
                else ""
            )

            text = f"{title} {message}".strip()

            if text:
                comments.append(text[:300])

        low_rating_pct = (
            float(
                (review_scores <= 2).mean() * 100
            )
            if not review_scores.empty
            else None
        )

        evidence["customer_feedback_evidence"] = {
            "review_count": int(len(review_df)),

            "average_review_score": (
                round(float(review_scores.mean()), 2)
                if not review_scores.empty
                else None
            ),

            "low_rating_pct": (
                round(low_rating_pct, 2)
                if low_rating_pct is not None
                else None
            ),

            "text_comment_count": len(comments),

            "sample_comments": comments[:5],

            "method":
                "Reviews joined to orders, customers and products "
                "for the target region, category and order month.",

            "interpretation":
                "Customer feedback is contextual evidence. "
                "It does not establish causation."
        }

    else:

        evidence["customer_feedback_evidence"] = {
            "review_count": 0,
            "average_review_score": None,
            "low_rating_pct": None,
            "text_comment_count": 0,
            "sample_comments": [],
            "method":
                "No matching customer reviews were found.",
            "interpretation":
                "No customer-feedback evidence is available "
                "for this investigation period."
        }

    analytics_runtime_ms = (
        time.perf_counter() - investigation_start
    ) * 1000

    # --------------------------------------------------
    # 7. Generate hypotheses
    # --------------------------------------------------

    hypothesis_llm_start = time.perf_counter()

    hypotheses = generate_hypotheses(
        evidence
    )

    hypothesis_llm_runtime_ms = (
        time.perf_counter() - hypothesis_llm_start
    ) * 1000

    total_runtime_ms = (
        time.perf_counter() - investigation_start
    ) * 1000

    if hypotheses is None:
        return {
            "case": top_case,
            "history": history.to_dict(
                orient="records"
            ),
            "analysis": analysis,
            "z_scores": z_scores,
            "hybrid": hybrid,
            "evidence": evidence,
            "evidence_sufficiency": evidence_sufficiency,
            "hypotheses": None,
            "nlp": None,
            "confidence": None,
            "recommendation": None,
            "business_summary": None,
            "runtime_telemetry": {
            "total_runtime_ms": round(
                   total_runtime_ms,
                    2
                ),

                "analytics_runtime_ms": round(
                    analytics_runtime_ms,
                    2
                ),

                "hypothesis_llm_runtime_ms": round(
                    hypothesis_llm_runtime_ms,
                    2
                ),

                "summary_llm_runtime_ms": 0,

                "llm_runtime_ms": round(
                    hypothesis_llm_runtime_ms,
                    2
                ),

                "llm_used": True,

                "decision_path":
                    "Evidence → LLM → No hypothesis",

                "evidence_sources":
                    len(evidence_lineage)
            },
        }

    # --------------------------------------------------
    # 8. NLP interpretation
    # --------------------------------------------------

    nlp_results = []

    for hypothesis in hypotheses.hypotheses:

        nlp_result = analyze_hypothesis_language(
            hypothesis
        )

        nlp_results.append({
            "statement": hypothesis.statement,
            "signals": nlp_result["signals"],
            "claim_type": nlp_result["claim_type"],
            "relationship": nlp_result["relationship"],
            "direction": nlp_result["direction"],
            "causal_claim": nlp_result["causal_claim"],
            "certainty": nlp_result["certainty"],
            "uncertainty_detected": nlp_result[
                "uncertainty_detected"
            ],
        })

    # --------------------------------------------------
    # 9. Select hypothesis
    # --------------------------------------------------

    selected_hypothesis = hypotheses.hypotheses[0]

    selected_nlp = analyze_hypothesis_language(
        selected_hypothesis
    )

    # --------------------------------------------------
    # 10. Confidence
    # --------------------------------------------------

    confidence = calculate_hypothesis_confidence(
        selected_hypothesis,
        evidence,
        selected_nlp
    )

    # --------------------------------------------------
    # 10B. Evidence sufficiency confidence adjustment
    # --------------------------------------------------

    if evidence_sufficiency["status"] == "LIMITED":

        original_score = confidence["confidence_score"]

        # Penalize confidence because the historical baseline
        # is small, even when the evidence points in one direction.
        adjusted_score = min(
            original_score * 0.75,
            0.60
        )

        confidence["confidence_score"] = round(
            adjusted_score,
            2
        )

        if adjusted_score >= 0.70:
            confidence["confidence_level"] = "HIGH"
        elif adjusted_score >= 0.50:
            confidence["confidence_level"] = "MEDIUM"
        else:
            confidence["confidence_level"] = "LOW"

        confidence.setdefault(
            "evidence_breakdown",
            []
        )

        confidence["evidence_breakdown"].append(
            (
                "Limited historical baseline",
                -1
            )
        )

        confidence["confidence_note"] = (
            "Confidence is reduced because only a limited "
            "historical baseline is available."
        )



    # ----------------------------------------------
    # 11. Recommendation
    # ----------------------------------------------

    recommendation = generate_recommendation(
        top_case,
        evidence,
        selected_hypothesis,
        confidence
    )

    # --------------------------------------------------
    # 12. Final LLM business summary
    # --------------------------------------------------

    summary_llm_start = time.perf_counter()

    business_summary = generate_business_summary(
        top_case,
        evidence,
        selected_hypothesis,
        selected_nlp,
        confidence,
        recommendation
    )

    summary_llm_runtime_ms = (
        time.perf_counter() - summary_llm_start
    ) * 1000

    llm_runtime_ms = (
        hypothesis_llm_runtime_ms
        + summary_llm_runtime_ms
    )

    total_runtime_ms = (
        time.perf_counter() - investigation_start
    ) * 1000

    # --------------------------------------------------
    # 13. Return complete investigation
    # --------------------------------------------------

    return {
        "case": top_case,

        "history": history.to_dict(orient="records"),

        "analysis": analysis,

        "z_scores": z_scores,

        "hybrid": hybrid,

        "driver_decomposition": driver_decomposition,

        "evidence_lineage": evidence_lineage,

        "evidence": evidence,

        "evidence_sufficiency": evidence_sufficiency,

        "hypotheses": [
            {
                "type": hypothesis.type,
                "statement": hypothesis.statement,
                "evidence_basis": hypothesis.evidence_basis,
                "unknowns": hypothesis.unknowns,
            }
            for hypothesis in hypotheses.hypotheses
        ],

        "nlp": nlp_results,

        "selected_hypothesis": {
            "type": selected_hypothesis.type,
            "statement": selected_hypothesis.statement,
        },

        "confidence": confidence,

        "recommendation": recommendation,

        "business_summary": business_summary,

        "runtime_telemetry": {
            "total_runtime_ms": round(
                total_runtime_ms,
                2
            ),

            "analytics_runtime_ms": round(
                analytics_runtime_ms,
                2
            ),

            "hypothesis_llm_runtime_ms": round(
                hypothesis_llm_runtime_ms,
                2
            ),

            "summary_llm_runtime_ms": round(
                summary_llm_runtime_ms,
                2
            ),

            "llm_runtime_ms": round(
                llm_runtime_ms,
                2
            ),

            "llm_used": True,

            "decision_path":
                "Evidence → Drivers → Hypothesis → Recommendation",

            "evidence_sources":
                len(evidence_lineage)
        },
    }
