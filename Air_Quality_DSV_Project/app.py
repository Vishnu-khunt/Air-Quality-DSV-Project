"""Interactive Streamlit dashboard for the Air Quality DSV project."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
CLEANED = ROOT / "outputs" / "cleaned_city_day.csv"
HEALTH = ROOT / "outputs" / "health_death_rate_long.csv"
LOCKDOWN = ROOT / "outputs" / "lockdown_city_comparison.csv"
SUMMARY = ROOT / "outputs" / "results_summary.json"

st.set_page_config(page_title="Indian Air Quality Explorer", page_icon="🌫️", layout="wide")
st.title("🌫️ Air Quality in Indian Cities (2015–2020)")
st.caption("Interactive analysis of pollution trends, seasonality, the available lockdown window, and air-pollution mortality.")

if not CLEANED.exists():
    st.error("Cleaned data not found. Run `python analysis.py` from the project folder first.")
    st.stop()

df = pd.read_csv(CLEANED, parse_dates=["Date"])
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
df["AQI"] = pd.to_numeric(df["AQI"], errors="coerce")
df["PM2.5"] = pd.to_numeric(df["PM2.5"], errors="coerce")

SEASONS = ["Winter", "Summer", "Monsoon", "Post-monsoon"]
POLLUTANTS = [c for c in ["PM2.5", "PM10", "NO", "NO2", "NOx", "NH3", "CO", "SO2", "O3", "Benzene", "Toluene", "Xylene", "AQI"] if c in df.columns]
cities = sorted(df["City"].dropna().unique().tolist())
years = sorted(df["Year"].dropna().astype(int).unique().tolist())

with st.sidebar:
    st.header("Filters")
    chosen_cities = st.multiselect("Cities (empty = all)", cities, default=[])
    yr_range = st.select_slider("Year range", options=years, value=(min(years), max(years)))
    pollutant = st.selectbox("Pollutant / measure", POLLUTANTS, index=POLLUTANTS.index("PM2.5") if "PM2.5" in POLLUTANTS else 0)
    season_choice = st.multiselect("Season", SEASONS, default=SEASONS)
    st.caption("Filters apply to Trends, Seasonality and Data quality. The lockdown tab always compares its available matched dates; the health tab uses the years available in the health file.")

filtered = df[df["Year"].between(yr_range[0], yr_range[1])].copy()
if chosen_cities:
    filtered = filtered[filtered["City"].isin(chosen_cities)]
if season_choice:
    filtered = filtered[filtered["Season"].isin(season_choice)]
else:
    filtered = filtered.iloc[0:0]

def mean_or_na(series, digits=1):
    value = pd.to_numeric(series, errors="coerce").mean()
    return f"{value:,.{digits}f}" if pd.notna(value) else "N/A"

def safe_chart(fig, key):
    st.plotly_chart(fig, use_container_width=True, key=key)

valid_aqi = filtered.dropna(subset=["AQI"])
city_means = valid_aqi.groupby("City")["AQI"].mean().dropna().sort_values(ascending=False)
poor_buckets = filtered["AQI_Bucket"].isin(["Poor", "Very Poor", "Severe"])
valid_bucket = filtered["AQI_Bucket"].notna()
poor_share = poor_buckets[valid_bucket].mean() * 100 if valid_bucket.any() else np.nan

k1, k2, k3, k4 = st.columns(4)
k1.metric("Mean AQI", mean_or_na(valid_aqi["AQI"]))
k2.metric("Highest mean-AQI city", str(city_means.index[0]) if len(city_means) else "N/A")
k3.metric("Observed city-days Poor or worse", f"{poor_share:.1f}%" if pd.notna(poor_share) else "N/A")
k4.metric("Rows in current selection", f"{len(filtered):,}")
st.caption("AQI metrics are calculated from existing AQI observations. 2020 is partial-year data, and the dashboard does not recalculate official AQI sub-indices.")

tabs = st.tabs(["Trends", "Seasonality", "Lockdown effect", "Health impact", "Data quality"])

with tabs[0]:
    st.subheader("Pollution trends")
    if filtered.empty:
        st.info("No records match these filters. Select at least one season and check the city/year filters.")
    else:
        left, right = st.columns(2)
        city_bar = (filtered.groupby("City", as_index=False)["AQI"].mean()
                    .dropna().sort_values("AQI", ascending=False).head(10))
        if not city_bar.empty:
            fig = px.bar(city_bar.sort_values("AQI"), x="AQI", y="City", orientation="h",
                         title="Highest mean AQI cities", color="AQI",
                         color_continuous_scale="OrRd",
                         hover_data={"AQI":":.1f"})
            fig.update_layout(yaxis_title="", xaxis_title="Mean AQI", coloraxis_colorbar_title="AQI")
            safe_chart(fig, "top_cities")
        else:
            st.info("No valid AQI values in this selection.")

        annual = filtered.groupby("Year", as_index=False).agg(
            mean_value=(pollutant, "mean"),
            valid_observations=(pollutant, "count")
        )
        fig = px.line(annual, x="Year", y="mean_value", markers=True,
                      title=f"Yearly mean {pollutant} (all selected cities)",
                      hover_data={"valid_observations":True, "mean_value":":.2f"})
        fig.update_traces(connectgaps=False)
        fig.update_layout(xaxis=dict(dtick=1), yaxis_title=f"Mean {pollutant}")
        safe_chart(fig, "overall_yearly_trend")

        # Keep city comparison readable: selected cities if provided; otherwise five cities
        # with the highest mean AQI in the filtered data.
        if chosen_cities:
            trend_cities = chosen_cities
        else:
            trend_cities = city_means.head(5).index.tolist()
        city_annual = (filtered[filtered["City"].isin(trend_cities)]
                       .groupby(["Year", "City"], as_index=False)["PM2.5"].mean())
        if not city_annual.empty:
            full_years = sorted(filtered["Year"].dropna().astype(int).unique())
            full_idx = pd.MultiIndex.from_product([full_years, trend_cities], names=["Year", "City"])
            city_annual = city_annual.set_index(["Year", "City"]).reindex(full_idx).reset_index()
            fig = px.line(city_annual, x="Year", y="PM2.5", color="City", markers=True,
                          title="Yearly mean PM2.5 by city (top 5, or selected cities)",
                          hover_data={"PM2.5":":.2f"})
            fig.update_traces(connectgaps=False)
            fig.update_layout(xaxis=dict(dtick=1), yaxis_title="Mean PM2.5")
            safe_chart(fig, "city_yearly_trend")
            st.caption("A line starts only where that city has valid PM2.5 observations. Missing years are kept as gaps, not replaced with zero.")
        st.markdown("**Recent rows with valid measurements shown first**")
        # Remove repeated column names: when pollutant == "PM2.5", the old list
        # included PM2.5 twice and pandas raised ValueError during sort_values().
        table_cols = list(dict.fromkeys(
            c for c in ["City", "Date", pollutant, "PM2.5", "AQI", "AQI_Bucket"]
            if c in filtered.columns
        ))
        sort_cols = list(dict.fromkeys(c for c in [pollutant, "Date"] if c in table_cols))
        display_df = filtered[table_cols].sort_values(
            by=sort_cols,
            ascending=[False] * len(sort_cols),
            na_position="last"
        )
        st.dataframe(display_df.head(300), use_container_width=True, hide_index=True)
        st.caption("The table shows up to 300 rows. Missing values are retained and displayed as empty cells.")

with tabs[1]:
    st.subheader("Seasonality")
    if filtered.empty:
        st.info("No records match these filters.")
    else:
        seasonal = (filtered.groupby("Season", observed=True)[pollutant]
                    .agg(["mean", "count"]).reindex(SEASONS).reset_index())
        seasonal = seasonal.rename(columns={"mean": "Mean value", "count": "Valid observations"})
        fig = px.bar(seasonal, x="Season", y="Mean value", title=f"Mean {pollutant} by season",
                     color="Season", hover_data={"Valid observations":True, "Mean value":":.2f"})
        fig.update_layout(showlegend=False, yaxis_title=f"Mean {pollutant}")
        safe_chart(fig, "seasonal_means")

        monthly = filtered.groupby(["City", "Month"])["PM2.5"].mean().reset_index()
        if not monthly.empty:
            heat = monthly.pivot(index="City", columns="Month", values="PM2.5").reindex(columns=range(1, 13))
            heat.columns = [pd.Timestamp(2000, int(m), 1).strftime("%b") for m in heat.columns]
            # Plot missing cells as a neutral gray sentinel; legend note clarifies it is not zero.
            z = heat.fillna(-1)
            colorscale = [
                [0.0, "#747b84"], [0.0039, "#747b84"],
                [0.004, "#fff7bc"], [0.25, "#fec44f"],
                [0.55, "#fe9929"], [0.78, "#ec7014"], [1.0, "#99000d"]
            ]
            fig = go.Figure(data=go.Heatmap(
                z=z.values, x=list(heat.columns), y=list(heat.index),
                colorscale=colorscale, zmin=-1, zmax=max(100, float(np.nanpercentile(heat.to_numpy(dtype=float), 95)) if heat.notna().any().any() else 100),
                colorbar=dict(title="PM2.5", tickmode="array", tickvals=[-1, 0, 50, 100, 150, 200], ticktext=["No data", "0", "50", "100", "150", "200"]),
                customdata=heat.values,
                hovertemplate="City: %{y}<br>Month: %{x}<br>Mean PM2.5: %{customdata:.2f}<extra></extra>"
            ))
            fig.update_layout(title="Mean PM2.5 by city and month", xaxis_title="Month", yaxis_title="City")
            safe_chart(fig, "monthly_heatmap")
            st.caption("Gray cells mean no valid PM2.5 average was available for that city-month. They do not mean zero pollution.")

with tabs[2]:
    st.subheader("COVID-19 lockdown-period comparison")
    st.warning("Coverage limitation: the supplied city_day.csv ends on 10 April 2020. This comparison covers 25 March–10 April only, matched to the same dates in 2019; it does not cover the full 25 March–30 June lockdown.")
    if LOCKDOWN.exists():
        lock = pd.read_csv(LOCKDOWN)
        if chosen_cities and not lock.empty:
            lock = lock[lock["City"].isin(chosen_cities)]
        if not lock.empty:
            lock = lock.sort_values("Percent change 2020 vs 2019")
            avg_change = lock["Percent change 2020 vs 2019"].mean()
            a, b, c = st.columns(3)
            a.metric("Cities compared", len(lock))
            b.metric("Mean city-level change", f"{avg_change:.1f}%")
            c.metric("Cities with a decrease", f"{(lock['Percent change 2020 vs 2019'] < 0).sum()} / {len(lock)}")
            fig = px.bar(lock, x="Percent change 2020 vs 2019", y="City", orientation="h",
                         color="Percent change 2020 vs 2019", color_continuous_scale="RdYlGn_r",
                         title="PM2.5 percentage change: available 2020 dates vs same 2019 dates",
                         hover_data={"2019":":.2f", "2020":":.2f", "Percent change 2020 vs 2019":":.1f"})
            fig.add_vline(x=0, line_dash="dash", line_color="white")
            fig.update_layout(yaxis_title="", xaxis_title="Percentage change (%)")
            safe_chart(fig, "lockdown_comparison")
            st.dataframe(lock.round(2), use_container_width=True, hide_index=True)
        else:
            st.info("No matching cities are available for this selection.")
    else:
        st.info("Run `python analysis.py` to create the lockdown comparison output.")

with tabs[3]:
    st.subheader("Air-pollution mortality")
    st.caption("World Bank indicator: age-standardized mortality attributed to household and ambient air pollution, per 100,000 population.")
    if HEALTH.exists():
        h = pd.read_csv(HEALTH)
        if not h.empty:
            available_years = sorted(h["Year"].dropna().astype(int).unique())
            if len(available_years) == 1:
                st.info(f"The supplied health file has values for {available_years[0]} only. A time-series line chart and a multi-year PM2.5/death-rate trendline are not statistically supported by this file.")
            latest = max(available_years)
            latest_df = h[h["Year"] == latest].sort_values("Death rate per 100,000", ascending=True)
            fig = px.bar(latest_df, x="Death rate per 100,000", y="Country Name", orientation="h",
                         title=f"Air-pollution mortality comparison ({latest})",
                         color="Death rate per 100,000", color_continuous_scale="OrRd",
                         hover_data={"Death rate per 100,000":":.1f"})
            fig.update_layout(yaxis_title="", xaxis_title="Age-standardized mortality per 100,000")
            safe_chart(fig, "health_country_comparison")
            st.dataframe(latest_df[["Country Name", "Death rate per 100,000"]].round(1),
                         use_container_width=True, hide_index=True)
            st.caption("This is a national mortality indicator, not a city-level death count. It cannot establish that pollution in a particular city caused a national mortality rate.")
        else:
            st.info("No matching health observations are available in health.csv.")
    else:
        st.info("Optional health data not found. Place health.csv in data/ and rerun analysis.py.")

    st.markdown("### Multi-year PM2.5 exposure context")
    st.write("The mortality dataset supplied with this project has only 2019 values. This chart uses a separate World Bank indicator for mean annual PM2.5 exposure, measured in micrograms per cubic meter, so it must not be interpreted as a death rate.")
    st.caption("Source: World Bank indicator EN.ATM.PM25.MC.M3. Requires an internet connection.")
    try:
        api_url = "https://api.worldbank.org/v2/country/IND;BGD;CHN;NPL;PAK/indicator/EN.ATM.PM25.MC.M3?format=json&date=1990:2023&per_page=2000"
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        payload = response.json()
        records = payload[1] if isinstance(payload, list) and len(payload) > 1 and payload[1] else []
        exp = pd.DataFrame([{"Country": r.get("country", {}).get("value"), "Year": int(r["date"]), "PM2.5 exposure (µg/m³)": r.get("value")} for r in records if r.get("value") is not None and r.get("date")])
        if exp.empty:
            st.info("The World Bank API returned no PM2.5 exposure observations. The local mortality comparison remains available.")
        else:
            exp = exp.sort_values(["Country", "Year"])
            fig = px.line(exp, x="Year", y="PM2.5 exposure (µg/m³)", color="Country", markers=True,
                          title="Mean annual PM2.5 exposure by country", hover_data={"Year": True, "PM2.5 exposure (µg/m³)": ":.2f"})
            fig.update_yaxes(rangemode="tozero")
            safe_chart(fig, "health_exposure_trend")
            st.caption(f"Available observations: {exp['Year'].min()}–{exp['Year'].max()}. Missing years are left as gaps. This national exposure indicator is not directly comparable to individual city-day readings.")
            st.dataframe(exp, use_container_width=True, hide_index=True)
    except (requests.RequestException, ValueError, TypeError, KeyError) as exc:
        st.warning("Could not retrieve multi-year PM2.5 exposure data. Check the internet connection and reload. The local 2019 mortality comparison is still available.")

with tabs[4]:
    st.subheader("Data quality and missing values")
    st.write("This section shows how much information is available after cleaning. Missing values are not treated as zero.")
    numeric_focus = [c for c in ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3", "AQI"] if c in filtered.columns]
    if filtered.empty:
        st.info("No records match these filters.")
    else:
        miss = pd.DataFrame({
            "Column": numeric_focus,
            "Missing rows": [int(filtered[c].isna().sum()) for c in numeric_focus],
            "Missing (%)": [round(float(filtered[c].isna().mean()*100), 2) for c in numeric_focus],
            "Valid rows": [int(filtered[c].notna().sum()) for c in numeric_focus],
        }).sort_values("Missing (%)", ascending=False)
        fig = px.bar(miss.sort_values("Missing (%)"), x="Missing (%)", y="Column", orientation="h",
                     title="Missing values by variable", color="Missing (%)",
                     color_continuous_scale="OrRd",
                     hover_data={"Missing rows":True, "Valid rows":True, "Missing (%)":":.2f"})
        fig.update_layout(yaxis_title="", xaxis_title="Missing rows (%)")
        safe_chart(fig, "missingness_chart")
        st.dataframe(miss, use_container_width=True, hide_index=True)
        st.metric("Missing PM2.5 values in current selection", f"{filtered['PM2.5'].isna().mean()*100:.1f}%")
        st.caption("Short internal pollutant gaps may have been interpolated. AQI is not interpolated or recalculated, and missing calendar dates that were absent from the original file are not automatically added.")
        if SUMMARY.exists():
            try:
                summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
                st.write("Dataset coverage")
                c1, c2, c3 = st.columns(3)
                c1.metric("Cities in source", summary.get("city_count", "N/A"))
                c2.metric("Rows after cleaning", f"{summary.get('rows_after_cleaning', 0):,}")
                c3.metric("Last date in source", summary.get("date_end", "N/A"))
            except (ValueError, OSError):
                pass

st.divider()
st.caption("Interpretation: observational analysis only. AQI is not recalculated from pollutant sub-indices, 2020 is partial-year data, and correlation does not prove causation.")
