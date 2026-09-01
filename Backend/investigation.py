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
)

from Backend.llm import (
    generate_hypotheses,
    generate_business_summary,
)

from Backend.nlp import analyze_hypothesis_language

from Backend.recommendation import generate_recommendation


def run_investigation(scenario="priority"):

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

    evidence_sufficiency = assess_evidence_sufficiency(
        history,
        top_case["month"]
    )

    # --------------------------------------------------
    # 2B. Evidence sufficiency gate
    # --------------------------------------------------

    if evidence_sufficiency["status"] == "INSUFFICIENT":

        reasons = evidence_sufficiency.get(
            "reasons",
            []
        )

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
                "unusual or to support a specific underlying explanation."
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
    # 7. Generate hypotheses
    # --------------------------------------------------

    hypotheses = generate_hypotheses(
        evidence
    )

    if hypotheses is None:
        return {
            "case": top_case,
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



    # --------------------------------------------------
    # 11. Recommendation
    # --------------------------------------------------

    recommendation = generate_recommendation(
        top_case,
        evidence,
        selected_hypothesis,
        confidence
    )

    # --------------------------------------------------
    # 12. Final LLM business summary
    # --------------------------------------------------

    business_summary = generate_business_summary(
        top_case,
        evidence,
        selected_hypothesis,
        selected_nlp,
        confidence,
        recommendation
    )

    # --------------------------------------------------
    # 13. Return complete investigation
    # --------------------------------------------------

    return {
        "case": top_case,

        "history": history.to_dict(orient="records"),

        "analysis": analysis,

        "z_scores": z_scores,

        "hybrid": hybrid,

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
    }
