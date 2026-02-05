from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Ethiopia Financial Inclusion Forecast", layout="wide")

# ---------- Paths ----------
ROOT = Path.cwd()
if not (ROOT / "data" / "processed").exists() and (ROOT.parent / "data" / "processed").exists():
    ROOT = ROOT.parent

PROCESSED = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw"

DATA_FILE = PROCESSED / "ethiopia_fi_unified_data_enriched.csv"
FORECAST_FILE = PROCESSED / "forecast_2025_2027.csv"

st.title("Forecasting Financial Inclusion in Ethiopia 🇪🇹")
st.caption("Selam Analytics — Interim dashboard for exploring trends, events, and forecasts (Access & Usage).")

# ---------- Load ----------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df["observation_date"] = pd.to_datetime(df["observation_date"], errors="coerce")
    return df

@st.cache_data
def load_forecast():
    f = pd.read_csv(FORECAST_FILE)
    return f

df = load_data()
obs = df[df["record_type"] == "observation"].copy()
events = df[df["record_type"] == "event"].copy()

forecast = None
if FORECAST_FILE.exists():
    forecast = load_forecast()

# ---------- Sidebar ----------
st.sidebar.header("Controls")
min_date = obs["observation_date"].min()
max_date = obs["observation_date"].max()

date_range = st.sidebar.date_input(
    "Observation date range",
    value=(min_date.date() if pd.notna(min_date) else None, max_date.date() if pd.notna(max_date) else None),
)

scenario = st.sidebar.selectbox("Forecast scenario", ["base", "pessimistic", "optimistic"], index=1)

# Filter by date range
if isinstance(date_range, tuple) and len(date_range) == 2 and date_range[0] and date_range[1]:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    obs_f = obs[(obs["observation_date"] >= start) & (obs["observation_date"] <= end)].copy()
    events_f = events[(events["observation_date"] >= start) & (events["observation_date"] <= end)].copy()
else:
    obs_f = obs.copy()
    events_f = events.copy()

# ---------- KPI Cards ----------
st.subheader("Overview")

def latest_value(code):
    x = obs[obs["indicator_code"] == code].dropna(subset=["value_numeric"]).sort_values("observation_date")
    if x.empty:
        return None, None
    return float(x["value_numeric"].iloc[-1]), x["observation_date"].iloc[-1].date()

col1, col2, col3, col4 = st.columns(4)

acc, acc_date = latest_value("ACC_OWNERSHIP")
mm, mm_date = latest_value("ACC_MM_ACCOUNT")
crossover, cross_date = latest_value("USG_CROSSOVER")
active_rate, ar_date = latest_value("USG_ACTIVE_RATE")

col1.metric("Access: Account Ownership (latest)", f"{acc:.1f}%" if acc is not None else "—", help=f"Date: {acc_date}" if acc_date else "")
col2.metric("Access: Mobile Money Account (latest)", f"{mm:.2f}%" if mm is not None else "—", help=f"Date: {mm_date}" if mm_date else "")
col3.metric("Usage: P2P/ATM Crossover (latest)", f"{crossover:.2f}" if crossover is not None else "—", help=f"Date: {cross_date}" if cross_date else "")
col4.metric("Usage: Active Rate (latest)", f"{active_rate:.2f}" if active_rate is not None else "—", help=f"Date: {ar_date}" if ar_date else "")

st.divider()

# ---------- Tabs ----------
tab1, tab2, tab3, tab4 = st.tabs(["Trends", "Events", "Forecasts", "Download"])

# ---------- Trends ----------
with tab1:
    st.subheader("Trends (Observations)")

    indicator_list = sorted(obs["indicator_code"].dropna().unique().tolist())
    default_inds = [c for c in ["ACC_OWNERSHIP", "USG_ACTIVE_RATE", "USG_CROSSOVER", "USG_TELEBIRR_USERS"] if c in indicator_list]
    selected = st.multiselect("Select indicators", indicator_list, default=default_inds)

    if selected:
        plot_df = obs_f[obs_f["indicator_code"].isin(selected)].dropna(subset=["observation_date", "value_numeric"]).copy()
        fig = px.line(
            plot_df,
            x="observation_date",
            y="value_numeric",
            color="indicator_code",
            markers=True,
            title="Selected indicators over time",
            labels={"observation_date": "Date", "value_numeric": "Value", "indicator_code": "Indicator"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select at least one indicator.")

    st.caption("Tip: Use the sidebar date range to focus on recent years.")

# ---------- Events ----------
with tab2:
    st.subheader("Events timeline")
    if events_f.empty:
        st.info("No events in the selected range.")
    else:
        ev = events_f.copy()
        # event title stored in `indicator` in your schema
        ev = ev.rename(columns={"indicator": "event_title", "observation_date": "event_date"})
        ev = ev.dropna(subset=["event_date"]).sort_values("event_date")

        fig = px.scatter(
            ev,
            x="event_date",
            y="category",
            hover_data=["event_title", "source_name", "confidence"],
            title="Cataloged events by category",
            labels={"event_date": "Event date", "category": "Event category"},
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(ev[["record_id", "category", "event_title", "event_date", "source_name", "confidence"]], use_container_width=True)

# ---------- Forecasts ----------
with tab3:
    st.subheader("Forecasts (2025–2027)")
    if forecast is None:
        st.warning("forecast_2025_2027.csv not found in data/processed. Run Task 4 notebook to generate it.")
    else:
        st.write(f"Scenario: **{scenario}**")

        # Build plot data
        years = forecast["year"]
        access_col = f"access_{scenario}"
        usage_col = f"usage_{scenario}"

        c1, c2 = st.columns(2)

        with c1:
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=years, y=forecast[access_col], mode="lines+markers", name="Access"))
            fig1.update_layout(title="Access forecast: Account Ownership (ACC_OWNERSHIP)", xaxis_title="Year", yaxis_title="% of adults")
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=years, y=forecast[usage_col], mode="lines+markers", name="Usage"))
            fig2.update_layout(title="Usage forecast: Active Rate (USG_ACTIVE_RATE)", xaxis_title="Year", yaxis_title="Rate / %")
            st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(forecast, use_container_width=True)

        # Progress toward 60% target visualization (simple)
        if "access_base" in forecast.columns:
            target = 60.0
            base_access_2027 = float(forecast.loc[forecast["year"] == 2027, "access_base"].values[0])
            st.markdown("### Progress toward 60% inclusion target (illustrative)")
            st.progress(min(max(base_access_2027 / target, 0), 1.0))
            st.caption(f"Base Access (2027): {base_access_2027:.1f}% vs Target: {target:.0f}%")

# ---------- Download ----------
with tab4:
    st.subheader("Download data")
    st.download_button(
        "Download enriched dataset (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="ethiopia_fi_unified_data_enriched.csv",
        mime="text/csv",
    )

    if forecast is not None:
        st.download_button(
            "Download forecast table (CSV)",
            data=forecast.to_csv(index=False).encode("utf-8"),
            file_name="forecast_2025_2027.csv",
            mime="text/csv",
        )

    st.caption("These files are generated/used in Tasks 1–4 and power the dashboard.")
