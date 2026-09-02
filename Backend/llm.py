import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from groq import RateLimitError
from pydantic import BaseModel, ValidationError


class Hypothesis(BaseModel):
    type: str
    statement: str
    evidence_basis: list[str]
    unknowns: list[str]

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class HypothesisResponse(BaseModel):
    hypotheses: list[Hypothesis]


groq_api_key = os.environ.get("GROQ_API_KEY")

if not groq_api_key:
    raise RuntimeError(
        "GROQ_API_KEY is missing. Check the .env file."
    )

client = Groq(api_key=groq_api_key)

def generate_hypotheses(evidence):
    """
    Generate structured investigation hypotheses
    from validated evidence.

    If the Groq quota is unavailable, return a
    deterministic evidence-grounded fallback.
    """

    if evidence is None:
        return None

    prompt = f"""
You are an investigation analyst.

You are given structured evidence produced by a
deterministic analytics system.

Your job is to formulate evidence-grounded
investigation hypotheses.

STRUCTURED EVIDENCE:

{json.dumps(evidence, default=str, indent=2)}

IMPORTANT RULES:

1. Use ONLY information contained in the evidence.

2. Do NOT invent operational causes such as:
   - supplier delays
   - shipment losses
   - stock write-offs
   - fraud
   - customer demand changes
   - reorder failures
   unless the evidence explicitly contains those facts.

3. Do NOT turn a possible explanation into a confirmed fact.

4. Do NOT claim causation from temporal correlation.

5. A hypothesis should describe a plausible relationship
   between signals that are actually present in the evidence.

6. Clearly identify what is known and what remains unknown.

7. If the available evidence cannot support a specific
   explanation, state that the underlying cause remains
   unknown and requires further investigation.

For each hypothesis return:

- type:
  A short category describing the hypothesis.

- statement:
  A concise, cautious hypothesis based only on
  the available evidence.

- evidence_basis:
  Specific facts from the supplied evidence that
  support why this hypothesis is worth investigating.

- unknowns:
  Important information that is not available and
  prevents the hypothesis from being treated as fact.

Do not generate explanations that require facts
outside the supplied evidence.

Prefer a small number of strong hypotheses over
many speculative hypotheses.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful business investigation "
                        "analyst. Ground every hypothesis in the "
                        "provided evidence."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "hypothesis_response",
                    "schema": HypothesisResponse.model_json_schema()
                }
            }
        )

        result = response.choices[0].message.content

        if result and result.strip():
            try:
                return HypothesisResponse.model_validate_json(result)

            except ValidationError as validation_error:
                print(
                    "WARNING: LLM returned invalid hypothesis structure."
                )
                print(validation_error) 

    except RateLimitError:
        print(
            "WARNING: Groq quota exhausted. "
            "Using deterministic hypothesis fallback."
        )

    # --------------------------------------------------
    # Deterministic fallback
    # --------------------------------------------------

    inventory = evidence.get("inventory_evidence", {})
    revenue = evidence.get("revenue_evidence", {})

    inventory_declined = (
        inventory.get("stock_change_pct", 0) < 0
    )

    revenue_declined = (
        revenue.get("deviation_pct", 0) < 0
    )

    hypotheses = []

    if inventory_declined and revenue_declined:

        hypotheses.append({
            "type": "Inventory Impact on Revenue",
            "statement": (
                "The rapid inventory decline may have contributed "
                "to the observed revenue shortfall during the "
                "case period."
            ),
            "evidence_basis": [
                "Inventory declined during the case period and "
                "revenue was below expected performance during "
                "the same period."
            ],
            "unknowns": [
                "The available evidence does not establish "
                "causation or identify the underlying operational "
                "cause of the inventory decline."
            ]
        })

    elif inventory_declined:

        hypotheses.append({
            "type": "Inventory Decline",
            "statement": (
                "The observed inventory decline warrants "
                "investigation to determine whether it reflects "
                "expected or unexpected stock movement."
            ),
            "evidence_basis": [
                "Inventory declined during the case period."
            ],
            "unknowns": [
                "The available evidence does not identify why "
                "inventory declined.",
                "It is unknown whether the movement was expected."
            ]
        })

    elif revenue_declined:

        hypotheses.append({
            "type": "Revenue Performance",
            "statement": (
                "The observed revenue shortfall warrants "
                "investigation to determine the underlying "
                "factors affecting performance."
            ),
            "evidence_basis": [
                "Revenue was below expected performance during "
                "the case period."
            ],
            "unknowns": [
                "The available evidence does not establish "
                "the underlying cause of the revenue shortfall."
            ]
        })

    else:

        hypotheses.append({
            "type": "Business Anomaly",
            "statement": (
                "The observed business signals warrant further "
                "investigation because the available evidence "
                "does not establish the underlying cause."
            ),
            "evidence_basis": [
                "The analytical pipeline identified a business "
                "signal requiring investigation."
            ],
            "unknowns": [
                "The available evidence is insufficient to "
                "identify a specific underlying cause."
            ]
        })

    return HypothesisResponse.model_validate({
        "hypotheses": hypotheses
    })

def generate_business_summary(
    case,
    evidence,
    hypothesis,
    nlp_result,
    confidence,
    recommendation
):
    """
    Generate a business-facing explanation from the
    completed analytical pipeline.

    The LLM is only responsible for communicating
    the results clearly. It must not invent evidence,
    change confidence, or claim unsupported causation.
    """
    inventory = evidence["inventory_evidence"]
    revenue = evidence["revenue_evidence"]
    
    prompt = f"""
You are a business intelligence analyst.

Create a concise business-facing investigation summary
using ONLY the information provided below.

Do not invent facts.
Do not introduce new causes.
Do not change the confidence level.
Do not claim causation unless causal_claim is explicitly True.

IMPORTANT:
Use numerical values exactly as provided.
Do not infer relationships between numbers yourself.

For inventory:
- If current_stock is greater than reorder_level,
  state that inventory is ABOVE the reorder level.
- If current_stock is less than reorder_level,
  state that inventory is BELOW the reorder level.
- Never describe inventory as below the reorder level
  when the supplied evidence says below_reorder is False.

Do not contradict the supplied evidence or recommendation.

CASE
----
Month: {case['month']}
Region: {case['region']}
Category: {case['product_category_name']}
Priority: {case['priority_score']}
Priority Level: {case['priority_level']}

EVIDENCE
--------
Current stock: {inventory['current_stock']}
Reorder level: {inventory['reorder_level']}
Below reorder level: {inventory['below_reorder']}

HYPOTHESIS
----------
Type: {hypothesis.type}
Statement: {hypothesis.statement}
Evidence Basis: {hypothesis.evidence_basis}
Unknowns: {hypothesis.unknowns}

NLP INTERPRETATION
------------------
Signals: {nlp_result['signals']}
Claim Type: {nlp_result['claim_type']}
Relationship: {nlp_result['relationship']}
Direction: {nlp_result['direction']}
Causal Claim: {nlp_result['causal_claim']}
Certainty: {nlp_result['certainty']}
Uncertainty Detected: {nlp_result['uncertainty_detected']}

CONFIDENCE
----------
Score: {confidence['confidence_score']}
Level: {confidence['confidence_level']}
Supporting Score: {confidence['supporting_score']}
Weakening Score: {confidence['weakening_score']}

RECOMMENDATION
--------------
Action: {recommendation['action']}
Urgency: {recommendation['urgency']}
Priority: {recommendation['priority']}
Next Steps: {recommendation['next_steps']}
Confidence Note: {recommendation['confidence_note']}
Causal Warning: {recommendation['causal_warning']}

Write the response using exactly these sections:

1. Executive Summary
2. Key Evidence
3. Investigation Hypothesis
4. Confidence
5. Recommended Action
6. Important Caveat

Keep the response concise and business-oriented.

The final response must clearly distinguish:
- observed facts
- possible explanations
- recommended actions

Do not introduce explanations that are not explicitly
present in the supplied hypothesis or evidence.

For example, do not say inventory "limited sales capacity"
unless that exact conclusion is supported by the supplied
evidence.

Prefer:
"The inventory decline may have contributed to the
revenue shortfall."

Do not add operational mechanisms that were not provided.

Do not present a hypothesis as a confirmed fact.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful business intelligence "
                        "analyst. Use only the supplied evidence."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            reasoning_effort="low",
            include_reasoning=False,
            max_completion_tokens=700
        )

        content = response.choices[0].message.content

        if content and content.strip():
            return content.strip()

    except RateLimitError:
        print("WARNING: Groq quota exhausted. Using deterministic business summary fallback.")

    # --------------------------------------------------
    # Deterministic fallback
    # --------------------------------------------------

    return f"""
1. Executive Summarys

In {case['month']}, the {case['region']} region's
{case['product_category_name']} category experienced
a significant inventory decline alongside weaker revenue
performance. Inventory remains above the reorder level,
but the magnitude of the inventory movement warrants
investigation.

2. Key Evidence

Current stock: {inventory['current_stock']}
Reorder level: {inventory['reorder_level']}
Below reorder level: {inventory['below_reorder']}

Inventory and revenue both declined during the case
period, with inventory showing the strongest statistical
movement.

3. Investigation Hypothesis

{hypothesis.statement}

4. Confidence

Confidence: {confidence['confidence_score']}
Level: {confidence['confidence_level']}

Supporting evidence score: {confidence['supporting_score']}
Weakening evidence score: {confidence['weakening_score']}

5. Recommended Action

{recommendation['action']}

Next steps:
{chr(10).join(
    f"- {step}" for step in recommendation['next_steps']
)}

6. Important Caveat

{recommendation['causal_warning']}
""".strip()