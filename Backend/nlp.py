import re


def analyze_hypothesis_language(hypothesis):
    """
    Interpret the language of an LLM-generated hypothesis.

    This function does NOT decide whether the hypothesis is true.
    It only extracts linguistic characteristics that can later
    be used by the confidence layer.
    """

    if hypothesis is None:
        return None

    statement = hypothesis.statement.lower()

    # --------------------------------------------------
    # 1. Identify business signals
    # --------------------------------------------------

    signals = []

    inventory_terms = [
        "inventory",
        "stock",
        "stock levels",
        "stock level",
        "inventory levels",
        "inventory level"
    ]

    revenue_terms = [
        "revenue",
        "sales",
        "sales revenue"
    ]

    if any(term in statement for term in inventory_terms):
        signals.append("inventory")

    if any(term in statement for term in revenue_terms):
        signals.append("revenue")

    # --------------------------------------------------
    # 2. Detect relationship
    # --------------------------------------------------

    causal_terms = [
        "caused",
        "cause",
        "causing",
        "led to",
        "resulted in",
        "resulting in",
        "because of",
        "due to",
        "driven by",
        "responsible for"
    ]

    impact_terms = [
        "contributing",
        "contribute",
        "contributed",
        "impact",
        "impacting",
        "affected",
        "affecting",
        "influenced",
        "influence",
        "limiting",
        "constrain",
        "constraining"
    ]

    correlation_terms = [
        "coincides",
        "coincided",
        "associated",
        "association",
        "relationship",
        "related",
        "correlated",
        "correlation",
        "simultaneous",
        "concurrent",
        "together"
    ]

    causal_claim = any(
        term in statement
        for term in causal_terms
    )

    impact_relationship = any(
        term in statement
        for term in impact_terms
    )

    correlation_relationship = any(
        term in statement
        for term in correlation_terms
    )

    if causal_claim:
        relationship = "causal"

    elif impact_relationship:
        relationship = "potential_impact"

    elif correlation_relationship:
        relationship = "correlation"

    else:
        relationship = "descriptive"

    # --------------------------------------------------
    # 3. Identify claim type
    # --------------------------------------------------

    priority_terms = [
        "priority",
        "priority score",
        "priority level",
        "high priority",
        "low priority",
        "medium priority"
    ]

    threshold_terms = [
        "reorder threshold",
        "reorder level",
        "threshold",
        "stock-out",
        "stockout",
        "stock out",
        "below reorder",
        "above reorder"
    ]

    statistical_terms = [
        "statistical",
        "statistically",
        "z-score",
        "z score",
        "normal variation",
        "normal range",
        "normal statistical",
        "extreme",
        "anomaly"
    ]

    if any(
        term in statement
        for term in priority_terms
    ):
        claim_type = "PRIORITY_EXPLANATION"

    elif any(
        term in statement
        for term in threshold_terms
    ):
        claim_type = "THRESHOLD_INTERPRETATION"

    elif any(
        term in statement
        for term in statistical_terms
    ):
        claim_type = "STATISTICAL_INTERPRETATION"

    elif (
        "inventory" in signals
        and "revenue" in signals
    ):
        claim_type = "SIGNAL_RELATIONSHIP"

    elif "inventory" in signals:
        claim_type = "INVENTORY_BEHAVIOR"

    elif "revenue" in signals:
        claim_type = "REVENUE_BEHAVIOR"

    else:
        claim_type = "GENERAL"

    # --------------------------------------------------
    # 4. Detect direction
    # --------------------------------------------------

    negative_terms = [
        "decline",
        "declined",
        "decrease",
        "decreased",
        "drop",
        "dropped",
        "shortfall",
        "negative",
        "fell",
        "fall",
        "reduction",
        "reduced",
        "lower",
        "below"
    ]

    positive_terms = [
        "increase",
        "increased",
        "growth",
        "grew",
        "higher",
        "above",
        "rise",
        "rose",
        "improvement"
    ]

    has_negative = any(
        term in statement
        for term in negative_terms
    )

    has_positive = any(
        term in statement
        for term in positive_terms
    )

    if has_negative and not has_positive:
        direction = "negative"

    elif has_positive and not has_negative:
        direction = "positive"

    elif has_negative and has_positive:
        direction = "mixed"

    else:
        direction = "neutral"

    # --------------------------------------------------
    # 5. Detect uncertainty / hedging
    # --------------------------------------------------

    uncertainty_terms = [
        "may",
        "might",
        "could",
        "possibly",
        "possible",
        "appears",
        "appear",
        "suggests",
        "suggest",
        "potential",
        "potentially",
        "likely",
        "unlikely"
    ]

    uncertainty_detected = any(
        re.search(
            rf"\b{re.escape(term)}\b",
            statement
        )
        for term in uncertainty_terms
    )

    if uncertainty_detected:
        certainty = "moderate"
    else:
        certainty = "high"

    # --------------------------------------------------
    # 6. Detect unsupported causal language
    # --------------------------------------------------

    unsupported_causal_claim = (
        causal_claim
        and len(signals) > 0
    )

    # --------------------------------------------------
    # 7. Return structured interpretation
    # --------------------------------------------------

    return {
        "signals": signals,
        "claim_type": claim_type,
        "relationship": relationship,
        "direction": direction,
        "causal_claim": causal_claim,
        "certainty": certainty,
        "uncertainty_detected": uncertainty_detected,
        "unsupported_causal_claim": unsupported_causal_claim
    }