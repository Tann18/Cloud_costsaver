import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_anomaly(df):
    if len(df) < 10:
        df["anomaly"] = 1
        return df

    model = IsolationForest(contamination=0.1)
    model.fit(df[["cpu", "cost"]])

    df["anomaly"] = model.predict(df[["cpu", "cost"]])

    return df