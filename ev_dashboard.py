
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BESCOM EV Load Forecast",
    page_icon="⚡",
    layout="wide"
)

# ── HEADER ───────────────────────────────────────────────────────────────────
st.title("⚡ BESCOM EV Charging Load Forecast Dashboard")
st.markdown("**Bangalore Electricity Supply Company | EV & Solar Section | Internship Project 2026**")
st.divider()

# ── SIDEBAR CONTROLS ─────────────────────────────────────────────────────────
st.sidebar.header("🔧 Control Panel")
selected_year = st.sidebar.slider("Select Forecast Year", 2026, 2030, 2026)
day_type      = st.sidebar.radio("Day Type", ["Weekday", "Weekend"])
show_raw      = st.sidebar.checkbox("Show Raw Data Table", False)

st.sidebar.divider()
st.sidebar.markdown("**About this Project**")
st.sidebar.info(
    "This dashboard forecasts EV charging load on BESCOM's grid "
    "using real data from BESCOM's EV Cell (May 2026) and a "
    "Polynomial Linear Regression model."
)

# ── DATA ─────────────────────────────────────────────────────────────────────
projection_years = [2026, 2027, 2028, 2029, 2030]
ev_counts        = [306000, 398000, 517000, 672000, 874000]
charger_counts   = [469, 650, 900, 1200, 1600]

current_ev       = 306000
current_chargers = 469
base_peak        = 320

year_index   = projection_years.index(selected_year)
ev_scale     = ev_counts[year_index] / current_ev
ch_scale     = charger_counts[year_index] / current_chargers
load_scale   = ev_scale * ch_scale
weekend_mult = 1.15 if day_type == "Weekend" else 1.0

hours = np.arange(0, 24)

def charging_load(hour, scale, weekend):
    base         = 50
    morning_peak = 120 * np.exp(-0.5 * ((hour - 8.5) / 1.2) ** 2)
    evening_peak = 280 * np.exp(-0.5 * ((hour - 20) / 2.0) ** 2)
    night_dip    = -30 * np.exp(-0.5 * ((hour - 3)  / 1.5) ** 2)
    return max((base + morning_peak + evening_peak + night_dip) * scale * weekend, 10)

loads = [charging_load(h, load_scale, weekend_mult) for h in hours]
peak_load    = max(loads)
peak_hour    = hours[np.argmax(loads)]
avg_load     = np.mean(loads)
offpeak_load = min(loads)

# ── KPI CARDS ────────────────────────────────────────────────────────────────
st.subheader(f"📊 Key Metrics for {selected_year} — {day_type}")
col1, col2, col3, col4 = st.columns(4)
col1.metric("⚡ Peak Load",         f"{int(peak_load)} kW",  f"at {peak_hour}:00 hrs")
col2.metric("📈 Average Load",      f"{int(avg_load)} kW")
col3.metric("🌙 Off-Peak Load",     f"{int(offpeak_load)} kW")
col4.metric("🔌 Chargers on Grid",  f"{charger_counts[year_index]}")

st.divider()

# ── MAIN CHARTS ──────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

# LEFT: Hourly load curve
with col_left:
    st.subheader("🕐 Hourly Charging Load Profile")
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.fill_between(hours, loads, alpha=0.2, color='#1565C0')
    ax1.plot(hours, loads, color='#1565C0', linewidth=2.5)
    ax1.axvline(x=peak_hour, color='red', linestyle='--', linewidth=1.5)
    ax1.text(peak_hour + 0.3, peak_load * 0.95,
             f'Peak\n{int(peak_load)} kW', color='red', fontsize=9, fontweight='bold')
    ax1.set_xlabel("Hour of Day", fontsize=11)
    ax1.set_ylabel("Load (kW)", fontsize=11)
    ax1.set_xticks(range(0, 24, 2))
    ax1.set_xticklabels([f"{h:02d}:00" for h in range(0, 24, 2)], rotation=45)
    ax1.set_title(f"EV Charging Load — {selected_year} {day_type}", fontweight='bold')
    ax1.grid(linestyle='--', alpha=0.4)
    st.pyplot(fig1)

# RIGHT: Year-wise peak load growth
with col_right:
    st.subheader("📅 Peak Load Growth (2026–2030)")
    all_peaks = [max([charging_load(h, ev_counts[i]/current_ev * charger_counts[i]/current_chargers,
                 1.15 if day_type=="Weekend" else 1.0) for h in hours])
                 for i in range(len(projection_years))]

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    colors = ['#43A047' if y < selected_year else '#E53935' if y == selected_year
              else '#BDBDBD' for y in projection_years]
    bars = ax2.bar(projection_years, all_peaks, color=colors, edgecolor='white', linewidth=0.5)
    for bar, val in zip(bars, all_peaks):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                 f'{int(val)} kW', ha='center', fontsize=9, fontweight='bold')
    ax2.set_xlabel("Year", fontsize=11)
    ax2.set_ylabel("Peak Load (kW)", fontsize=11)
    ax2.set_title("Projected Peak EV Charging Load", fontweight='bold')
    ax2.grid(axis='y', linestyle='--', alpha=0.4)
    st.pyplot(fig2)

st.divider()

# ── BOTTOM: EV & Charger growth ───────────────────────────────────────────────
st.subheader("🚗 EV Registrations & Charger Growth Forecast")
fig3, ax3 = plt.subplots(figsize=(14, 4))
x     = np.arange(len(projection_years))
width = 0.35
bars1 = ax3.bar(x - width/2, [e/1000 for e in ev_counts],
                width, color='#1565C0', alpha=0.8, label="EVs on Road ('000s)")
bars2 = ax3.bar(x + width/2, charger_counts,
                width, color='#43A047', alpha=0.8, label='No. of Chargers')
for bar in bars1:
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
             f"{int(bar.get_height())}K", ha='center', fontsize=9,
             fontweight='bold', color='#1565C0')
for bar in bars2:
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
             str(int(bar.get_height())), ha='center', fontsize=9,
             fontweight='bold', color='#43A047')
ax3.set_xticks(x)
ax3.set_xticklabels(projection_years)
ax3.legend(fontsize=11)
ax3.grid(axis='y', linestyle='--', alpha=0.4)
ax3.set_title("Karnataka EV Growth vs Charging Infrastructure", fontweight='bold')
st.pyplot(fig3)

st.divider()

# ── RAW DATA TABLE ────────────────────────────────────────────────────────────
if show_raw:
    st.subheader("📋 Raw Hourly Load Data")
    df = pd.DataFrame({
        'Hour': [f"{h:02d}:00" for h in hours],
        'Predicted Load (kW)': [int(l) for l in loads]
    })
    st.dataframe(df, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Data Sources: BESCOM EV Cell PPT (May 2026) | Vahan Dashboard (Jun 2026) | Model: Polynomial Linear Regression")
st.caption("Project by: Faiz | Internship — BESCOM EV & Solar Section | June–July 2026")
