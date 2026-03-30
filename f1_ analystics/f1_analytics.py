import fastf1
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# -------------------------------
# 1. Setup & Load Data
# -------------------------------
os.makedirs("f1_cache", exist_ok=True)
fastf1.Cache.enable_cache("f1_cache")

print("Loading session...")
session = fastf1.get_session(2023, 1, 'R')
session.load()

laps = session.laps.copy()

# -------------------------------
# 2. Data Cleaning
# -------------------------------
print("\nCleaning data...")

# Remove missing lap times
laps = laps.dropna(subset=["LapTime"])

# Remove incomplete sector data
laps = laps.dropna(subset=[
    "Sector1Time", "Sector2Time", "Sector3Time"
])

# Create pit stop feature
laps["HasPitStop"] = (
    laps["PitOutTime"].notna() | laps["PitInTime"].notna()
)

# -------------------------------
# 3. Basic Info
# -------------------------------
print("\nDataset Info:")
print(laps.info())

print("\nMissing Values:")
print(laps.isnull().sum())

print("\nDrivers:")
print(laps['Driver'].unique())

# -------------------------------
# 4. Analysis
# -------------------------------

# Fastest lap overall
fastest_lap = laps.loc[laps['LapTime'].idxmin()]
print("\n🏁 Fastest Lap Overall:")
print(fastest_lap[['Driver', 'LapTime', 'LapNumber']])

# Total laps per driver
laps_per_driver = laps.groupby("Driver")["LapNumber"].count().sort_values(ascending=False)
print("\nTotal Laps by Driver:")
print(laps_per_driver)

# Fastest lap per driver
fastest_per_driver = laps.groupby("Driver")["LapTime"].min().sort_values()
print("\nFastest Lap by Driver:")
print(fastest_per_driver)

# Average lap time
avg_lap = laps.groupby("Driver")["LapTime"].mean().dt.total_seconds().sort_values()
print("\nAverage Lap Time:")
print(avg_lap)

# Tyre performance
tyre_perf = laps.groupby("Compound")["LapTime"].mean()
print("\nTyre Performance:")
print(tyre_perf)

# Pit strategy
stints = laps.groupby("Driver")["Stint"].max()
print("\nStints per Driver:")
print(stints)

# Sector performance
sector_perf = laps.groupby("Driver")[[
    "Sector1Time", "Sector2Time", "Sector3Time"
]].mean()

print("\nSector Performance:")
print(sector_perf)

# -------------------------------
# 5. Visualization
# -------------------------------
print("\nGenerating chart...")

plt.figure(figsize=(12,6))

avg_lap.plot(kind="bar")

plt.title("Average Lap Time per Driver", fontsize=14)
plt.xlabel("Driver")
plt.ylabel("Lap Time (seconds)")
plt.xticks(rotation=90)

plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig("outputs/avg_lap_time.png")
plt.show()