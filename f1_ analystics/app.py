import streamlit as st
import fastf1
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="F1 Analytics Dashboard", layout="wide")

st.title(" F1 Race Analytics Dashboard")

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data(year, gp, session_type):
    os.makedirs("f1_cache", exist_ok=True)
    fastf1.Cache.enable_cache("f1_cache")

    session = fastf1.get_session(year, gp, session_type)
    session.load()
    
    laps = session.laps.copy()
    
    # Clean data
    laps = laps.dropna(subset=["LapTime"])
    laps = laps.dropna(subset=["Sector1Time", "Sector2Time", "Sector3Time"])
    
    laps["LapTime_sec"] = laps["LapTime"].dt.total_seconds()
    
    return laps

# -------------------------------
# Sidebar Inputs
# -------------------------------
st.sidebar.header(" Filters")

year = st.sidebar.selectbox("Select Year", [2023, 2022, 2021])
gp = st.sidebar.number_input("Grand Prix Round (e.g. 1)", min_value=1, max_value=22, value=1)
session_type = st.sidebar.selectbox("Session", ['R', 'Q', 'FP1'])

# -------------------------------
# Load
# -------------------------------
with st.spinner("Loading F1 Data..."):
    laps = load_data(year, gp, session_type)

# -------------------------------
# Metrics
# -------------------------------
st.subheader(" Key Insights")

col1, col2, col3 = st.columns(3)

fastest_lap = laps.loc[laps['LapTime_sec'].idxmin()]

col1.metric(" Fastest Driver", fastest_lap['Driver'])
col2.metric(" Fastest Lap (s)", round(fastest_lap['LapTime_sec'], 2))
col3.metric(" Total Laps", len(laps))

# -------------------------------
# Avg Lap Time Chart
# -------------------------------
st.subheader(" Average Lap Time per Driver")

avg_lap = laps.groupby("Driver")["LapTime_sec"].mean().sort_values()

fig, ax = plt.subplots()
avg_lap.plot(kind="bar", ax=ax)

ax.set_ylabel("Lap Time (seconds)")
ax.set_xlabel("Driver")
ax.set_title("Average Lap Time")
ax.tick_params(axis='x', rotation=90)

st.pyplot(fig)

# -------------------------------
# Driver Comparison
# -------------------------------
st.subheader("Driver Comparison")

drivers = st.multiselect("Select Drivers", options=avg_lap.index.tolist())

if drivers:
    filtered = laps[laps["Driver"].isin(drivers)]
    
    fig2, ax2 = plt.subplots()
    
    for driver in drivers:
        driver_laps = filtered[filtered["Driver"] == driver]
        ax2.plot(driver_laps["LapNumber"], driver_laps["LapTime_sec"], label=driver)
    
    ax2.set_xlabel("Lap Number")
    ax2.set_ylabel("Lap Time (seconds)")
    ax2.legend()
    
    st.pyplot(fig2)

# -------------------------------
# Tyre Strategy
# -------------------------------
st.subheader("Tyre Performance")

tyre_perf = laps.groupby("Compound")["LapTime_sec"].mean()

st.bar_chart(tyre_perf)

# -------------------------------
# Raw Data
# -------------------------------
st.subheader(" Raw Data")
st.dataframe(laps.head(50))