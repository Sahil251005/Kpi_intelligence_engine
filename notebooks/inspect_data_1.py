import pandas as pd
import os

DATA_PATH = "data/raw"

for file in os.listdir(DATA_PATH):
    if file.endswith(".csv"):
        path = os.path.join(DATA_PATH, file)

        df = pd.read_csv(path)

        print("\n" + "=" * 60)
        print("FILE:", file)
        print("ROWS:", len(df))
        print("COLUMNS:", len(df.columns))
        print("COLUMN NAMES:")
        print(list(df.columns))