def generate_recommendation(
    case,
    evidence,
    hypothesis,
    confidence
):
    """
    Generate an evidence-driven business recommendation.

    The recommendation is based on:
    - business priority
    - dominant signal
    - statistical anomalies
    - cross-signal behavior
    - hypothesis type
    - hypothesis confidence

    This function does not create new evidence or claim causation.
    """

    if (
        case is None
        or evidence is None
        or hypothesis is None
        or confidence is None
    ):
        return None

    business = evidence["business_evidence"]
    revenue = evidence["revenue_evidence"]
    inventory = evidence["inventory_evidence"]
    cross_signal = evidence["cross_signal_evidence"]

    # --------------------------------------------------
    # 1. Basic case information
    # --------------------------------------------------

    month = case["month"]
    region = case["region"]
    category = case["product_category_name"]

    priority = business["priority_level"]
    priority_score = business["priority_score"]

    dominant_signal = cross_signal["dominant_signal"]

    confidence_level = confidence["confidence_level"]
    confidence_score = confidence["confidence_score"]

    claim_type = confidence.get(
        "claim_type",
        getattr(hypothesis, "type", "UNKNOWN")
    )

    # --------------------------------------------------
    # 2. Identify important business signals
    # --------------------------------------------------

    inventory_extreme = (
        inventory["statistical_status"] == "EXTREME"
    )

    revenue_extreme = (
        revenue["statistical_status"] == "EXTREME"
    )

    inventory_declined = (
        cross_signal["inventory_declined"]
    )

    revenue_declined = (
        cross_signal["revenue_declined"]
    )

    same_period = (
        cross_signal["same_case_period"]
    )

    below_reorder = (
        inventory["below_reorder"]
    )

    # --------------------------------------------------
    # 3. Build evidence strength
    # --------------------------------------------------

    signal_strength = 0
    supporting_factors = []
    weakening_factors = []

    if inventory_extreme:
        signal_strength += 3
        supporting_factors.append(
            "Inventory movement is statistically extreme."
        )

    if revenue_extreme:
        signal_strength += 3
        supporting_factors.append(
            "Revenue movement is statistically extreme."
        )

    if inventory_declined:
        signal_strength += 1
        supporting_factors.append(
            "Inventory declined during the case period."
        )

    if revenue_declined:
        signal_strength += 1
        supporting_factors.append(
            "Revenue declined during the case period."
        )

    if same_period and inventory_declined and revenue_declined:
        signal_strength += 2
        supporting_factors.append(
            "Inventory and revenue declined during the same period."
        )

    if dominant_signal == "INVENTORY":
        signal_strength += 2
        supporting_factors.append(
            "Inventory is the dominant business signal."
        )

    elif dominant_signal == "REVENUE":
        signal_strength += 2
        supporting_factors.append(
            "Revenue is the dominant business signal."
        )

    if below_reorder:
        signal_strength += 2
        supporting_factors.append(
            "Current inventory is below the reorder level."
        )

    else:
        weakening_factors.append(
            "Inventory is currently above the reorder level."
        )

    # --------------------------------------------------
    # 4. Determine recommended action
    # --------------------------------------------------

    # Strong inventory signal
    if (
        dominant_signal == "INVENTORY"
        and inventory_extreme
    ):

        action = (
            "Investigate inventory depletion and "
            "replenishment activity."
        )

        next_steps = [
            "Review inventory movement records.",
            "Review replenishment timing and quantities.",
            "Check whether stock reductions were expected.",
        ]

    # Strong revenue signal
    elif (
        dominant_signal == "REVENUE"
        and revenue_extreme
    ):

        action = (
            "Investigate the underlying drivers of "
            "the revenue anomaly."
        )

        next_steps = [
            "Review sales performance for the affected period.",
            "Check relevant business and marketing drivers.",
            "Compare the anomaly with historical behavior.",
        ]

    # Both signals are important
    elif (
        inventory_declined
        and revenue_declined
        and same_period
    ):

        action = (
            "Investigate the relationship between "
            "inventory movement and revenue decline."
        )

        next_steps = [
            "Review inventory movement during the case period.",
            "Review sales and revenue drivers.",
            "Validate whether the two changes are operationally related.",
        ]

    # No sufficiently strong signal
    else:

        action = (
            "Continue monitoring the case and gather "
            "additional evidence."
        )

        next_steps = [
            "Monitor future KPI movements.",
            "Gather additional operational evidence.",
        ]

    # --------------------------------------------------
    # 5. Determine urgency
    # --------------------------------------------------

    if priority == "HIGH" and signal_strength >= 5:

        urgency = "IMMEDIATE"

    elif priority in ("HIGH", "MEDIUM") and signal_strength >= 3:

        urgency = "PRIORITIZED"

    else:

        urgency = "MONITOR"

    # --------------------------------------------------
    # 6. Confidence-aware recommendation wording
    # --------------------------------------------------

    if confidence_level == "HIGH":

        confidence_note = (
            "The available evidence strongly supports "
            "this investigation."
        )

    elif confidence_level == "MEDIUM":

        confidence_note = (
            "The available evidence provides moderate "
            "support and should be validated."
        )

    else:

        confidence_note = (
            "The available evidence is limited; "
            "additional validation is recommended."
        )

    # --------------------------------------------------
    # 7. Causality safeguard
    # --------------------------------------------------

    causal_warning = None

    if getattr(hypothesis, "type", None) == "causal":

        causal_warning = (
            "The hypothesis involves causation. "
            "The current evidence should not be treated "
            "as proof of a causal relationship."
        )

    elif confidence_level != "HIGH":

        causal_warning = (
            "The available evidence does not establish "
            "causation; further validation is required."
        )

    # --------------------------------------------------
    # 8. Final recommendation
    # --------------------------------------------------

    return {
        "case": {
            "month": month,
            "region": region,
            "category": category
        },

        "action": action,

        "urgency": urgency,

        "priority": priority,

        "priority_score": priority_score,

        "confidence": {
            "score": confidence_score,
            "level": confidence_level
        },

        "reason": supporting_factors,

        "weakening_factors": weakening_factors,

        "next_steps": next_steps,

        "confidence_note": confidence_note,

        "causal_warning": causal_warning,

        "signal_strength": signal_strength
    }