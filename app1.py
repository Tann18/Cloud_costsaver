import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import os

# 🔥 PATHS
DATA_PATH = r"C:\Users\tanma\OneDrive\Desktop\cloud-cost-ai\data\data.csv"
LOG_PATH = r"C:\Users\tanma\OneDrive\Desktop\cloud-cost-ai\logs\actions.log"

# 💰 Conversion
USD_TO_INR = 83

st.set_page_config(layout="wide")

# 🎨 SAME UI STYLE
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0e1117;
    color: #ffffff;
}
.metric-card {
    background: #1c1f26;
    padding: 15px;
    border-radius: 12px;
}
.alert-box {
    background: #3a1f1f;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.section-title {
    font-size: 22px;
    font-weight: bold;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# 🎛️ SIDEBAR
st.sidebar.title(" Control Panel")

refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 2, 10, 5)
show_cpu = st.sidebar.checkbox("Show CPU Graph", True)
show_cost = st.sidebar.checkbox("Show Cost Graph", True)
show_distribution = st.sidebar.checkbox("Show Cost Distribution", True)

currency = st.sidebar.selectbox(" Currency", ["INR (₹)", "USD ($)"])

if currency == "INR (₹)":
    rate = USD_TO_INR
    symbol = "₹"
else:
    rate = 1
    symbol = "$"

# HEADER
st.title(" Cloud Cost Intelligence Dashboard")
st.caption("🇮🇳 AI-powered cloud monitoring • anomaly detection • auto-optimization")

# LOAD DATA
if not os.path.exists(DATA_PATH):
    st.warning("Waiting for data...")
    st.stop()

df = pd.read_csv(DATA_PATH)

if df.empty:
    st.warning("No data yet...")
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"])

# 🔥 CORE VALUES
current_cost_usd = df["cost"].iloc[-1]
current_cpu = df["cpu"].iloc[-1]

# 🔥 INDUSTRY-STYLE SAVINGS LOGIC
recent_data = df.tail(20)

original_cost_usd = recent_data["cost"].sum()

# Focus only on anomalies for optimization
anomalies = recent_data[recent_data["anomaly"] == -1]

# realistic optimization: only 20% of anomaly cost reduced
reduction = anomalies["cost"].sum() * 0.2

optimized_cost_usd = original_cost_usd - reduction

# ensure optimized cost never negative
optimized_cost_usd = max(optimized_cost_usd, 0)

# REAL SAVINGS
saved_usd = original_cost_usd - optimized_cost_usd

# Convert currency
current_cost = current_cost_usd * rate
saved = saved_usd * rate

# 🔥 HARD CAP (IMPORTANT)
saved = min(saved, current_cost * 0.8)

# EXTRA METRICS
avg_cpu = df["cpu"].mean()
max_cpu = df["cpu"].max()
min_cpu = df["cpu"].min()

anomaly_count = len(df[df["anomaly"] == -1])

status = "Anomaly" if df.iloc[-1]["anomaly"] == -1 else "Normal"

# 📊 KPI ROW (UNCHANGED UI)
col1, col2, col3, col4 = st.columns(4)

col1.metric(" Instantaneous Current Cost", f"{symbol}{current_cost:,.2f}")
col2.metric(" CPU Usage", f"{current_cpu:.0f}%")
col3.metric(" Estimated Savings", f"{symbol}{saved:,.2f}", "Optimized")

if status == "Anomaly":
    col4.metric(" Status", status)
else:
    col4.metric("Status", status)

# 📊 EXTRA METRICS ROW
col5, col6, col7, col8 = st.columns(4)

col5.metric(" Avg CPU", f"{avg_cpu:.1f}%")
col6.metric(" Max CPU", f"{max_cpu:.0f}%")
col7.metric(" Min CPU", f"{min_cpu:.0f}%")
col8.metric(" Anomalies", anomaly_count)

# 📈 COST GRAPH
if show_cost:
    st.markdown('<div class="section-title">📊 Cost Over Time</div>', unsafe_allow_html=True)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["cost"] * rate,
        mode="lines",
        name="Cost",
        line=dict(width=3)
    ))

    anomalies_plot = df[df["anomaly"] == -1]

    fig.add_trace(go.Scatter(
        x=anomalies_plot["timestamp"],
        y=anomalies_plot["cost"] * rate,
        mode="markers",
        name="Anomaly",
        marker=dict(color="red", size=10)
    ))

    fig.update_layout(
        template="plotly_dark",
        height=400,
        yaxis_title=f"Cost ({symbol})"
    )

    st.plotly_chart(fig, use_container_width=True)

#  CPU GRAPH
if show_cpu:
    st.markdown('<div class="section-title"> CPU Usage Trend</div>', unsafe_allow_html=True)

    fig_cpu = go.Figure()

    fig_cpu.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["cpu"],
        mode="lines",
        name="CPU",
        line=dict(width=3)
    ))

    fig_cpu.update_layout(
        template="plotly_dark",
        height=400
    )

    st.plotly_chart(fig_cpu, use_container_width=True)

#  COST DISTRIBUTION
if show_distribution:
    st.markdown('<div class="section-title"> Cost Distribution</div>', unsafe_allow_html=True)

    fig_dist = px.histogram(df, x="cost", nbins=20)
    fig_dist.update_layout(template="plotly_dark")

    st.plotly_chart(fig_dist, use_container_width=True)

# ALERTS
st.markdown('<div class="section-title"> Recent Alerts</div>', unsafe_allow_html=True)

alerts = df[df["anomaly"] == -1].tail(5)

if alerts.empty:
    st.success("No anomalies detected")
else:
    for _, row in alerts.iterrows():
        st.markdown(f"""
        <div class="alert-box">
        <b>{row['timestamp']}</b><br>
        Cost spike detected<br>
        CPU: {row['cpu']}%
        </div>
        """, unsafe_allow_html=True)

# ⚡ ACTION LOG
st.markdown('<div class="section-title">⚡ Actions Taken</div>', unsafe_allow_html=True)

if os.path.exists(LOG_PATH):
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        logs = f.readlines()

    if logs:
        st.code("".join(logs[-10:]), language="text")
    else:
        st.info("No actions yet")
else:
    st.warning("Log file not found")

#  SYSTEM INSIGHTS
st.markdown('<div class="section-title"> System Insights</div>', unsafe_allow_html=True)

if anomaly_count > 5:
    st.warning("Frequent anomalies detected — consider scaling policies")
elif avg_cpu > 70:
    st.warning("High average CPU — system under heavy load")
else:
    st.success("System operating within normal parameters")

# 🔄 AUTO REFRESH
time.sleep(refresh_rate)
st.rerun()