import pandas as pd
from datetime import datetime
import time
import os

from utils.simulator import get_cpu_usage
from anomaly import detect_anomaly
from explain import explain_issue
from actions import auto_fix
from alert import send_alert


# 🔥 FULL PATHS
DATA_PATH = r"C:\Users\tanma\OneDrive\Desktop\cloud-cost-ai\data\data.csv"
LOG_PATH = r"C:\Users\tanma\OneDrive\Desktop\cloud-cost-ai\logs\actions.log"


# 🟢 STEP 1 — Collect data
def collect_data():
    cpu = get_cpu_usage()
    cost = cpu * 0.05

    new_data = {
        "timestamp": datetime.now(),
        "cpu": cpu,
        "cost": cost,
        "anomaly": 1
    }

    df = pd.DataFrame([new_data])

    file_exists = os.path.isfile(DATA_PATH)
    df.to_csv(DATA_PATH, mode='a', header=not file_exists, index=False)

    return new_data


# 🟢 STEP 2 — Log actions (SAFE UTF-8 + NO EMOJI CRASH)
def log_action(message):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {message}\n")
    except:
        # fallback (remove problematic chars)
        safe_message = message.encode("ascii", "ignore").decode()
        with open(LOG_PATH, "a") as f:
            f.write(f"[{datetime.now()}] {safe_message}\n")


# 🟢 STEP 3 — Main loop
def run():
    print("Monitoring started...\n")

    while True:
        collect_data()

        try:
            df = pd.read_csv(DATA_PATH)
        except:
            print("Waiting for data file...")
            time.sleep(5)
            continue

        if df.empty:
            print("No data yet...")
            time.sleep(5)
            continue

        df = detect_anomaly(df)
        df.to_csv(DATA_PATH, index=False)

        latest = df.iloc[-1]

        if latest["anomaly"] == -1:
            reason = explain_issue(latest)
            action = auto_fix(latest["cpu"])

            message = f"""
ALERT

CPU: {latest['cpu']}
Cost: {latest['cost']}

Reason: {reason}
Action Taken: {action}
"""

            send_alert(message)

            log_action(f"{reason} -> {action}")

            print("\nALERT")
            print(f"CPU: {latest['cpu']}")
            print(f"Cost: {latest['cost']}")
            print(f"Reason: {reason}")
            print(f"Action Taken: {action}")

        else:
            print(f"Normal: {latest['cpu']}")

        time.sleep(5)


if __name__ == "__main__":
    run()