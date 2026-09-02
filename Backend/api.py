from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text
from typing import Optional

from Backend.investigation import run_investigation
from Backend.database import get_engine

class FeedbackRequest(BaseModel):
    case_month: str
    region: str
    product_category: str
    warehouse: Optional[str] = None

    usefulness: str
    driver_assessment: str

    comment: Optional[str] = None


app = FastAPI(
    title="KPI Intelligence Engine",
    description="Backend API for KPI investigation and intelligence",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "KPI Intelligence Engine API is running"
    }


@app.get("/investigation")
def investigation(scenario: str = "priority"):

    try:
        if scenario == "insufficient":
            result = run_investigation(scenario="insufficient")

        elif scenario == "limited":
            result = run_investigation(scenario="limited")

        elif scenario == "sparse":
            result = run_investigation(scenario="sparse")

        else:
            result = run_investigation()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="No investigation case found."
            )

        case = result["case"]
        evidence = result["evidence"]
        z_scores = result["z_scores"]
        hybrid = result["hybrid"]
        confidence = result["confidence"]
        recommendation = result["recommendation"]

        driver_decomposition = result.get(
            "driver_decomposition"
        )

        evidence_lineage = result.get(
            "evidence_lineage",
            []
        )

        runtime_telemetry = result.get(
            "runtime_telemetry",
            {
                "total_runtime_ms": 0,
                "analytics_runtime_ms": 0,
                "hypothesis_llm_runtime_ms": 0,
                "summary_llm_runtime_ms": 0,
                "llm_runtime_ms": 0,
                "llm_used": False,
                "decision_path": "UNKNOWN",
                "evidence_sources": 0,
            }
        )

        evidence_sufficiency = result.get(
            "evidence_sufficiency",
            {
                "status": "UNKNOWN",
                "baseline_months": 0,
                "minimum_required": 2,
                "reasons": []
            }
        )
                        

        # --------------------------------------------------
        # Clean frontend-friendly response
        # --------------------------------------------------

        return {
            "case": {
                "month": str(case["month"]),
                "region": case["region"],
                "category": case["product_category_name"],
                "warehouse": case["warehouse_location"]
            },

            "history": [
                {
                    "month": str(row["month"]),
                    "region": row["region"],
                    "product_category_name": row["product_category_name"],
                    "revenue": float(row["revenue"]),
                    "expected_revenue": float(row["expected_revenue"]),
                    "revenue_deviation_pct": float(
                        row["revenue_deviation_pct"]
                    ),
                    "current_stock": int(row["current_stock"]),
                    "reorder_level": int(row["reorder_level"]),
                    "stock_change_pct": float(
                        row["stock_change_pct"]
                    ),
                    "inventory_status": row["inventory_status"],
                    "business_signal": row["business_signal"],
                    "priority_score": int(row["priority_score"]),
                    "priority_level": row["priority_level"],
                }
                for row in result["history"]
            ],

            "evidence_sufficiency": evidence_sufficiency,

            "runtime_telemetry": runtime_telemetry,       

            "priority": {
                "score": case["priority_score"],
                "level": case["priority_level"]
            },

            "key_metrics": {
                "revenue": {
                    "actual": case["revenue"],
                    "expected": case["expected_revenue"],
                    "deviation_pct": case["revenue_deviation_pct"],
                    "z_score": (
                        float(z_scores["revenue_z_score"])
                        if z_scores is not None
                        else None
                    )
                },

                "inventory": {
                    "current_stock": case["current_stock"],
                    "reorder_level": case["reorder_level"],
                    "stock_change_pct": case["stock_change_pct"],
                    "z_score": (
                        float(z_scores["stock_z_score"])
                        if z_scores is not None
                        else None
                    ),
                    "status": case["inventory_status"],
                    "below_reorder": case["below_reorder"]
                }
            },

            "signals": {
                "revenue_declined": (
                    evidence.get(
                        "cross_signal_evidence",
                        {}
                    ).get(
                        "revenue_declined",
                        False
                    )
                ),

                "inventory_declined": (
                    evidence.get(
                        "cross_signal_evidence",
                        {}
                    ).get(
                        "inventory_declined",
                        False
                    )
                ),

                "dominant_signal": (
                    evidence.get(
                        "cross_signal_evidence",
                        {}
                    ).get(
                        "dominant_signal",
                        "UNKNOWN"
                    )
                )
            },

            "driver_decomposition": driver_decomposition,

            "evidence_lineage": evidence_lineage,

            "hypothesis": result[
                "selected_hypothesis"
            ],

            "confidence": {
                "score": confidence[
                    "confidence_score"
                ],
                "level": confidence[
                    "confidence_level"
                ],
                "supporting_score": confidence[
                    "supporting_score"
                ],
                "weakening_score": confidence[
                    "weakening_score"
                ]
            },

            "recommendation": recommendation,

            "business_summary": result[
                "business_summary"
            ]
        }

    except HTTPException:
        raise

    except Exception as e:
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/feedback")
def submit_feedback(feedback: FeedbackRequest):

    allowed_usefulness = {
        "USEFUL",
        "NOT_USEFUL",
    }

    allowed_driver_assessments = {
        "SUPPORTED",
        "PARTIALLY_SUPPORTED",
        "NOT_SUPPORTED",
    }

    if feedback.usefulness not in allowed_usefulness:
        raise HTTPException(
            status_code=400,
            detail="Invalid usefulness value.",
        )

    if feedback.driver_assessment not in allowed_driver_assessments:
        raise HTTPException(
            status_code=400,
            detail="Invalid driver assessment value.",
        )

    try:

        with get_engine().begin() as connection:

            result = connection.execute(
                text("""
                    INSERT INTO analyst_feedback (
                        case_month,
                        region,
                        product_category,
                        warehouse,
                        usefulness,
                        driver_assessment,
                        comment
                    )
                    VALUES (
                        :case_month,
                        :region,
                        :product_category,
                        :warehouse,
                        :usefulness,
                        :driver_assessment,
                        :comment
                    )
                    RETURNING
                        feedback_id,
                        created_at
                """),
                {
                    "case_month": feedback.case_month,
                    "region": feedback.region,
                    "product_category": feedback.product_category,
                    "warehouse": feedback.warehouse,
                    "usefulness": feedback.usefulness,
                    "driver_assessment": feedback.driver_assessment,
                    "comment": feedback.comment,
                },
            )

            row = result.fetchone()

        return {
            "status": "SUCCESS",
            "message": "Analyst feedback recorded.",
            "feedback_id": row.feedback_id,
            "created_at": row.created_at,
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save feedback: {str(e)}",
        )