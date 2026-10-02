"""
app.py - RFM Customer Segmentation Dashboard (Streamlit)
----------------------------------------------------------
Run from the project root:
    streamlit run dashboard/app.py

Reads reports/rfm_customer_scores.csv (produced by
notebooks/rfm_analysis.py) and displays it as an interactive
dashboard for marketing / business stakeholders.
"""

import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="RFM Customer Segmentation", layout="wide")

st.title("Customer Segmentation Dashboard (RFM Analysis)")
st.caption("Recency, Frequency, Monetary scoring to identify Champions, At-Risk, and New customers")


@st.cache_data
def load_data():
    return pd.read_csv("reports/rfm_customer_scores.csv")


try:
    rfm = load_data()
except FileNotFoundError:
    st.error(
        "reports/rfm_customer_scores.csv not found. "
        "Run `python3 notebooks/rfm_analysis.py` from the project root first."
    )
    st.stop()

# ---------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------
st.sidebar.header("Filters")
segments = st.sidebar.multiselect(
    "Segment",
    options=sorted(rfm["segment"].unique()),
    default=sorted(rfm["segment"].unique())
)
filtered = rfm[rfm["segment"].isin(segments)]

# ---------------------------------------------------------
# KPI row
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", f"{filtered['customer_id'].nunique():,}")
col2.metric("Total Revenue", f"₹{filtered['monetary'].sum():,.0f}")
col3.metric("Avg Recency (days)", f"{filtered['recency_days'].mean():.0f}")
col4.metric("Avg Orders / Customer", f"{filtered['frequency'].mean():.1f}")

st.divider()

# ---------------------------------------------------------
# Charts
# ---------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    seg_counts = filtered["segment"].value_counts().reset_index()
    seg_counts.columns = ["segment", "customers"]
    fig1 = px.bar(seg_counts, x="segment", y="customers", title="Customers per Segment",
                  color="segment")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    seg_revenue = filtered.groupby("segment")["monetary"].sum().reset_index()
    fig2 = px.pie(seg_revenue, names="segment", values="monetary", title="Revenue Share by Segment")
    st.plotly_chart(fig2, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    fig3 = px.scatter(
        filtered, x="recency_days", y="monetary", color="segment", size="frequency",
        title="Recency vs Monetary (bubble size = Frequency)",
        hover_data=["customer_id"]
    )
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    fig4 = px.histogram(filtered, x="rfm_total_score", nbins=13, title="RFM Total Score Distribution")
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ---------------------------------------------------------
# Actionable customer list (what a retention/marketing team would use)
# ---------------------------------------------------------
st.subheader("Customer List (action-ready)")
st.dataframe(
    filtered[[
        "customer_id", "segment", "recency_days", "frequency",
        "monetary", "r_score", "f_score", "m_score", "rfm_total_score"
    ]].sort_values("rfm_total_score", ascending=False),
    use_container_width=True,
    height=400
)

st.download_button(
    "Download filtered list as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="rfm_filtered_customers.csv",
    mime="text/csv"
)
