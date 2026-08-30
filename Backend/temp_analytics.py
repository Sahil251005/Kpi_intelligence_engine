from investigation import run_investigation


result = run_investigation()


if result is None:

    print("No investigation case found.")

else:

    print("=== INVESTIGATION RESULT ===")

    print("\nCASE:")
    print(result["case"])

    print("\nCONFIDENCE:")
    print(result["confidence"])

    print("\nRECOMMENDATION:")
    print(result["recommendation"])

    print("\nFINAL BUSINESS SUMMARY:")
    print(result["business_summary"])