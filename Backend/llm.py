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