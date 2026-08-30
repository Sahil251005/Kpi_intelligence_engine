from Backend.analytics import (
    get_top_investigation_case,
    get_case_history,
    analyze_case_history,
    calculate_z_scores,
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


def run_investigation():
    """
    Run the complete KPI investigation pipeline.

    Returns a structured dictionary containing:
    - case
    - historical analysis
    - z-score analysis
    - hybrid assessment
    - evidence
    - hypotheses
    - NLP interpretation
    - confidence
    - recommendation
    - final business summary
    """

    # --------------------------------------------------
    # 1. Get highest-priority investigation case
    # --------------------------------------------------

    top_case = get_top_investigation_case()

    if top_case is None:
        return None

    # --------------------------------------------------
    # 2. Get historical case data
    # --------------------------------------------------

    history = get_case_history(
        top_case["region"],
        top_case["product_category_name"]
    )

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

        "analysis": analysis,

        "z_scores": z_scores,

        "hybrid": hybrid,

        "evidence": evidence,

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