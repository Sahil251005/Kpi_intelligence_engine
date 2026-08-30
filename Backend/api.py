from fastapi import FastAPI, HTTPException

from Backend.investigation import run_investigation


app = FastAPI(
    title="KPI Intelligence Engine",
    description="Backend API for KPI investigation and intelligence",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "KPI Intelligence Engine API is running"
    }


@app.get("/investigation")
def investigation():

    try:
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

            "priority": {
                "score": case["priority_score"],
                "level": case["priority_level"]
            },

            "key_metrics": {
                "revenue": {
                    "actual": case["revenue"],
                    "expected": case["expected_revenue"],
                    "deviation_pct": case["revenue_deviation_pct"],
                    "z_score": float(
                        z_scores["revenue_z_score"]
                    )
                },

                "inventory": {
                    "current_stock": case["current_stock"],
                    "reorder_level": case["reorder_level"],
                    "stock_change_pct": case["stock_change_pct"],
                    "z_score": float(
                        z_scores["stock_z_score"]
                    ),
                    "status": case["inventory_status"],
                    "below_reorder": case["below_reorder"]
                }
            },

            "signals": {
                "revenue_declined": evidence[
                    "cross_signal_evidence"
                ]["revenue_declined"],

                "inventory_declined": evidence[
                    "cross_signal_evidence"
                ]["inventory_declined"],

                "dominant_signal": hybrid[
                    "dominant_signal"
                ]
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