from analytics import (
    get_top_investigation_case,
    get_case_history,
    analyze_case_history,
    calculate_z_scores,
    build_hybrid_assessment,
    build_evidence,
    calculate_hypothesis_confidence
)
from recommendation import generate_recommendation
from llm import (
    generate_hypotheses,
    generate_business_summary
)
from nlp import analyze_hypothesis_language

# --------------------------------------------------
# 1. Get the highest-priority investigation case
# --------------------------------------------------

top_case = get_top_investigation_case()

if top_case is None:

    print("No investigation case found.")

else:

    print("=== TOP INVESTIGATION CASE ===")

    print(f"Month: {top_case['month']}")
    print(f"Region: {top_case['region']}")
    print(f"Category: {top_case['product_category_name']}")
    print(f"Priority: {top_case['priority_score']}")
    print(f"Level: {top_case['priority_level']}")


    # --------------------------------------------------
    # 2. Retrieve historical case data
    # --------------------------------------------------

    history = get_case_history(
        top_case["region"],
        top_case["product_category_name"]
    )

    print("\n=== CASE HISTORY ===")

    print(
        history.to_string(index=False)
    )


    # --------------------------------------------------
    # 3. Historical analysis
    # --------------------------------------------------

    analysis = analyze_case_history(
        history,
        top_case["month"]
    )

    print("\n=== HISTORICAL ANALYSIS ===")

    if analysis is None:

        print(
            "Not enough historical data for comparison."
        )

    else:

        for key, value in analysis.items():

            print(
                f"{key}: {value}"
            )


    # --------------------------------------------------
    # 4. Statistical anomaly analysis
    # --------------------------------------------------

    z_scores = calculate_z_scores(
        history,
        top_case["month"]
    )

    print("\n=== Z-SCORE ANALYSIS ===")

    if z_scores is None:

        print(
            "Not enough historical data for "
            "z-score calculation."
        )

    else:

        for key, value in z_scores.items():

            print(
                f"{key}: {value}"
            )


    # --------------------------------------------------
    # 5. Hybrid assessment
    # --------------------------------------------------

    hybrid = build_hybrid_assessment(
        top_case,
        z_scores
    )

    print("\n=== HYBRID ASSESSMENT ===")

    if hybrid is None:

        print(
            "Unable to build hybrid assessment."
        )

    else:

        for key, value in hybrid.items():

            print(
                f"{key}: {value}"
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

    print("\n=== EVIDENCE ===")

    if evidence is None:

        print(
            "Unable to build evidence."
        )

    else:

        for section, values in evidence.items():

            print(
                f"\n--- {section.upper()} ---"
            )

            if isinstance(values, dict):

                for key, value in values.items():

                    print(
                        f"{key}: {value}"
                    )

            else:

                print(values)


# --------------------------------------------------
# 7. LLM Hypothesis Generation
# --------------------------------------------------

hypotheses = generate_hypotheses(
    evidence
)

print("\n=== LLM HYPOTHESES ===")

if hypotheses is None:
    print("Unable to generate hypotheses.")

else:
    for i, hypothesis in enumerate(
        hypotheses.hypotheses,
        start=1
    ):
        print(f"\n--- HYPOTHESIS {i} ---")

        print(
            f"Type: {hypothesis.type}"
        )

        print(
            f"Statement: {hypothesis.statement}"
        )

        print("\nEvidence basis:")

        for item in hypothesis.evidence_basis:
            print(f"- {item}")

        print("\nUnknowns:")

        for item in hypothesis.unknowns:
            print(f"- {item}")


# --------------------------------------------------
# 8. NLP + Confidence
# --------------------------------------------------

print("\n=== NLP HYPOTHESIS INTERPRETATION ===")

if hypotheses is None:

    print("No hypotheses available.")

else:

    for i, hypothesis in enumerate(
        hypotheses.hypotheses,
        start=1
    ):

        # ------------------------------------------
        # NLP interpretation
        # ------------------------------------------

        nlp_result = analyze_hypothesis_language(
            hypothesis
        )

        print(
            f"\n--- HYPOTHESIS {i} ---"
        )

        print(
            f"Statement: {hypothesis.statement}"
        )

        print(
            f"Signals: "
            f"{nlp_result['signals']}"
        )

        print(
            f"Claim type: "
            f"{nlp_result['claim_type']}"
        )

        print(
            f"Relationship: "
            f"{nlp_result['relationship']}"
        )

        print(
            f"Direction: "
            f"{nlp_result['direction']}"
        )

        print(
            f"Causal claim: "
            f"{nlp_result['causal_claim']}"
        )

        print(
            f"Certainty: "
            f"{nlp_result['certainty']}"
        )

        print(
            f"Uncertainty detected: "
            f"{nlp_result['uncertainty_detected']}"
        )


        # ------------------------------------------
        # Confidence
        # ------------------------------------------

        confidence = calculate_hypothesis_confidence(
            hypothesis,
            evidence,
            nlp_result
        )

        print(
            "\n=== CONFIDENCE ==="
        )

        print(
            f"Supporting score: "
            f"{confidence['supporting_score']}"
        )

        print(
            f"Weakening score: "
            f"{confidence['weakening_score']}"
        )

        print(
            f"Confidence score: "
            f"{confidence['confidence_score']}"
        )

        print(
            f"Confidence level: "
            f"{confidence['confidence_level']}"
        )

        print("\nEvidence weighting:")

        for description, weight in confidence[
            "evidence_breakdown"
        ]:

            sign = "+" if weight > 0 else ""

            print(
                f"{sign}{weight}: "
                f"{description}"
            )
# --------------------------------------------------
# 9. Recommendation
# --------------------------------------------------

print("\n=== RECOMMENDATION ===")

if hypotheses is None:
    print("No recommendation available.")

else:

    # For now, use the first hypothesis
    selected_hypothesis = hypotheses.hypotheses[0]

    nlp_result = analyze_hypothesis_language(
        selected_hypothesis
    )

    confidence = calculate_hypothesis_confidence(
        selected_hypothesis,
        evidence,
        nlp_result
    )

    recommendation = generate_recommendation(
        top_case,
        evidence,
        selected_hypothesis,
        confidence
    )

    if recommendation is None:

        print("Unable to generate recommendation.")

    else:

        print(
            f"Action: "
            f"{recommendation['action']}"
        )

        print(
            f"Urgency: "
            f"{recommendation['urgency']}"
        )

        print(
            f"Priority: "
            f"{recommendation['priority']}"
        )

        print(
            f"Confidence: "
            f"{recommendation['confidence']['level']}"
        )

        print("\nReason:")

        for reason in recommendation["reason"]:
            print(f"- {reason}")

        print("\nNext steps:")

        for step in recommendation["next_steps"]:
            print(f"- {step}")

        if recommendation["causal_warning"]:
            print(
                f"\nCaution: "
                f"{recommendation['causal_warning']}"
            )
# --------------------------------------------------
# 10. Final LLM Business Summary
# --------------------------------------------------

print("\n=== FINAL BUSINESS SUMMARY ===")

if (
    hypotheses is None
    or recommendation is None
):

    print("Unable to generate business summary.")

else:

    final_summary = generate_business_summary(
        top_case,
        evidence,
        selected_hypothesis,
        nlp_result,
        confidence,
        recommendation
    )

    print(final_summary)