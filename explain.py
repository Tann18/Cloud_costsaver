def explain_issue(row):
    if row["cpu"] > 80:
        return "High CPU usage causing cost spike"
    elif row["cpu"] < 5:
        return "Instance idle but running"
    elif row["cost"] > 3:
        return "Sudden cost spike"
    return "Normal behavior"