from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from Backend.investigation import run_investigation


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
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )