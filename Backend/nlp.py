import re


def analyze_hypothesis_language(hypothesis):
    """
    Interpret the language of an LLM-generated hypothesis.

    This function does NOT decide whether the hypothesis is true.
    It identifies what the hypothesis is claiming so that the
    confidence layer can evaluate the relevant evidence.
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
    # 2. Detect uncertainty / hedging
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
    # 3. Detect investigation / conditional language
    # --------------------------------------------------

    investigation_terms = [
        "determine if",
        "determine whether",
        "investigate whether",
        "investigate if",
        "assess whether",
        "assess if",
        "evaluate whether",
        "evaluate if",
        "check whether",
        "check if",
        "test whether",
        "test if",
        "whether"
    ]

    investigation_language = any(
        term in statement
        for term in investigation_terms
    )

    # --------------------------------------------------
    # 4. Detect causal language
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

    causal_language_detected = any(
        term in statement
        for term in causal_terms
    )

    # --------------------------------------------------
    # 4a. Detect negated / uncertain causal language
    # --------------------------------------------------

    non_causal_patterns = [
        "may not be due to",
        "might not be due to",
        "could not be due to",
        "may not be caused by",
        "might not be caused by",
        "could not be caused by",
        "not caused by",
        "not due to",
        "unlikely to be caused by",
        "unlikely to be due to"
    ]

    non_causal_language = any(
        phrase in statement
        for phrase in non_causal_patterns
    )

    # A causal word does not automatically mean
    # the hypothesis is making a causal claim.
    #
    # Example:
    # "Inventory caused revenue decline."
    # -> causal claim
    #
    # "Determine whether inventory caused revenue decline."
    # -> investigation, not causal claim
    #
    # "Revenue may not be due to inventory issues."
    # -> negated/uncertain, not causal claim

    causal_claim = (
        causal_language_detected
        and not investigation_language
        and not non_causal_language
    )

    # --------------------------------------------------
    # 5. Detect potential-impact relationship
    # --------------------------------------------------

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
        "constraining",
        "may affect",
        "may impact",
        "likely contributed",
        "could contribute",
        "might contribute"
    ]

    impact_relationship = any(
        term in statement
        for term in impact_terms
    )

    # --------------------------------------------------
    # 6. Detect correlation / association
    # --------------------------------------------------

    correlation_terms = [
        "coincides",
        "coincided",
        "associated",
        "association",
        "relationship",
        "related to",
        "linked to",
        "correlated",
        "correlation",
        "simultaneous",
        "together"
    ]

    correlation_relationship = any(
        term in statement
        for term in correlation_terms
    )

    # --------------------------------------------------
    # 7. Detect statistical interpretation
    # --------------------------------------------------

    statistical_terms = [
        "statistically",
        "statistical",
        "z-score",
        "z score",
        "normal statistical range",
        "normal range",
        "statistical range",
        "statistical variation",
        "statistical status",
        "extreme anomaly",
        "statistically extreme",
        "statistically normal",
        "normal variation",
        "anomaly"
    ]

    statistical_interpretation = any(
        term in statement
        for term in statistical_terms
    )

    # --------------------------------------------------
    # 8. Determine relationship
    # --------------------------------------------------

    if causal_claim:
        relationship = "causal"

    elif impact_relationship:
        relationship = "potential_impact"

    elif correlation_relationship:
        relationship = "correlation"

    else:
        relationship = "descriptive"

    # --------------------------------------------------
    # 9. Determine claim type
    # --------------------------------------------------
    #
    # Relationship claims are checked first only when
    # the sentence is actually relationship-focused.
    #
    # Statistical interpretation gets priority when
    # the sentence explicitly focuses on statistical
    # behavior.
    # --------------------------------------------------

    relationship_focused = (
        len(signals) >= 2
        and (
            impact_relationship
            or correlation_relationship
            or causal_claim
        )
    )

    if relationship_focused and not statistical_interpretation:
        claim_type = "SIGNAL_RELATIONSHIP"

    elif statistical_interpretation:
        claim_type = "STATISTICAL_INTERPRETATION"

    elif "inventory" in signals:
        claim_type = "INVENTORY_INTERPRETATION"

    elif "revenue" in signals:
        claim_type = "REVENUE_INTERPRETATION"

    else:
        claim_type = "OTHER"

    # --------------------------------------------------
    # 10. Detect direction
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
        "below",
        "depletion",
        "depleted"
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
    # 11. Detect unsupported causal language
    # --------------------------------------------------

    unsupported_causal_claim = (
        causal_claim
        and len(signals) >= 2
    )

    # --------------------------------------------------
    # 12. Return structured interpretation
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