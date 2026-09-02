import pandas as pd

import Backend.investigation as investigation


# --------------------------------------------------
# Fake investigation case
# --------------------------------------------------

fake_case = {
    "month": pd.Timestamp("2018-10-01"),
    "region": "TEST",
    "product_category_name": "abstention_test",
    "warehouse_location": "TEST-Warehouse",

    "revenue": 10000,
    "expected_revenue": 15000,
    "revenue_deviation_pct": -33.33,

    "current_stock": 100,
    "reorder_level": 200,
    "stock_change_pct": -50.00,
    "inventory_status": "CRITICAL",
    "below_reorder": True,

    "business_signal": "TEST_ABSTENTION",

    "priority_score": 999,
    "priority_level": "HIGH",
}


# --------------------------------------------------
# Fake history
# --------------------------------------------------
# Only the target month exists.
# Therefore there are ZERO historical observations
# before the target month.

fake_history = pd.DataFrame([
    {
        "month": pd.Timestamp("2018-10-01"),
        "region": "TEST",
        "product_category_name": "abstention_test",

        "revenue": 10000,
        "expected_revenue": 15000,
        "revenue_deviation_pct": -33.33,

        "current_stock": 100,
        "reorder_level": 200,
        "stock_change_pct": -50.00,

        "inventory_status": "CRITICAL",
        "business_signal": "TEST_ABSTENTION",

        "priority_score": 999,
        "priority_level": "HIGH",
    }
])


# --------------------------------------------------
# Replace database calls temporarily
# --------------------------------------------------

investigation.get_top_investigation_case = (
    lambda: fake_case
)

investigation.get_case_history = (
    lambda region, product_category_name:
        fake_history
)


# --------------------------------------------------
# Run actual investigation engine
# --------------------------------------------------

result = investigation.run_investigation()


# --------------------------------------------------
# Display result
# --------------------------------------------------

print("\n==============================")
print("ABSTENTION TEST RESULT")
print("==============================")

print(
    "Evidence sufficiency:",
    result["evidence_sufficiency"]
)

print(
    "Selected hypothesis:",
    result["selected_hypothesis"]
)

print(
    "Confidence:",
    result["confidence"]
)

print(
    "Recommendation:",
    result["recommendation"]
)

print("\n==============================")