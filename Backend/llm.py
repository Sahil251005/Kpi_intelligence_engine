import json
import os

from groq import Groq
from pydantic import BaseModel


class Hypothesis(BaseModel):
    type: str
    statement: str
    evidence_basis: list[str]
    unknowns: list[str]


class HypothesisResponse(BaseModel):
    hypotheses: list[Hypothesis]


client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)


def generate_hypotheses(evidence):
    """
    Generate structured investigation hypotheses
    from validated evidence.
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

    return HypothesisResponse.model_validate_json(result)
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

    prompt = f"""
You are a business intelligence analyst.

Create a concise business-facing investigation summary
using ONLY the information provided below.

Do not invent facts.
Do not introduce new causes.
Do not change the confidence level.
Do not claim causation unless causal_claim is explicitly True.

CASE
----
Month: {case['month']}
Region: {case['region']}
Category: {case['product_category_name']}
Priority: {case['priority_score']}
Priority Level: {case['priority_level']}

EVIDENCE
--------
{evidence}

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
        max_tokens=700
    )

    return response.choices[0].message.content