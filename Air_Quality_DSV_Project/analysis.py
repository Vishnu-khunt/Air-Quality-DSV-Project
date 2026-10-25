"""End-to-end analysis for Air Quality in Indian Cities (2015-2020)."""
from pathlib import Path
import json
import warnings
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

warnings.filterwarnings("ignore", category=FutureWarning)
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
FIG = OUT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

POLLUTANTS = ["PM2.5", "PM10", "NO", "NO2", "NOx", "NH3", "CO", "SO2", "O3", "Benzene", "Toluene", "Xylene"]
CORR_COLS = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3", "AQI"]
AQI_ORDER = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
COUNTRY_NAMES = ["India", "China", "Pakistan", "Bangladesh", "Nepal", "United States", "United Kingdom", "Brazil"]

def interpolate_only_short_gaps(series, max_gap=7):
    """Linearly interpolate internal missing runs only when the whole run is <= max_gap."""
    result = series.copy()
    missing = result.isna().to_numpy()
    i = 0
    while i < len(result):
        if not missing[i]:
            i += 1
            continue
        j = i
        while j < len(result) and missing[j]:
            j += 1
        run_length = j - i
        # Only internal gaps with observed values on both sides are interpolated.
        if run_length <= max_gap and i > 0 and j < len(result):
            left, right = result.iloc[i - 1], result.iloc[j]
            if pd.notna(left) and pd.notna(right):
                result.iloc[i:j] = np.linspace(left, right, run_length + 2)[1:-1]
        i = j
    return result

def aqi_bucket(value):
    """Re-label existing AQI values using the project's requested Indian AQI bands."""
    if pd.isna(value):
        return np.nan
    if value < 0:
        return np.nan
    if value <= 50:
        return "Good"
    if value <= 100:
        return "Satisfactory"
    if value <= 200:
        return "Moderate"
    if value <= 300:
        return "Poor"
    if value <= 400:
        return "Very Poor"
    return "Severe"

def load_and_clean():
    source = DATA / "city_day.csv"
    if not source.exists():
        raise FileNotFoundError(f"Missing {source}. Put city_day.csv inside the data folder.")
    df = pd.read_csv(source)
    required = {"City", "Date", "AQI"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"city_day.csv is missing required columns: {sorted(missing)}")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["City", "Date"])
    before_duplicates = len(df)
    df = df.drop_duplicates(subset=["City", "Date"], keep="first")
    duplicate_rows_removed = before_duplicates - len(df)
    numeric_cols = [c for c in POLLUTANTS + ["AQI"] if c in df.columns]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        # Negative measurements are invalid; convert them to missing, not zero.
        df.loc[df[col] < 0, col] = np.nan
    df = df.sort_values(["City", "Date"]).reset_index(drop=True)
    interpolated_counts = {}
    for col in POLLUTANTS:
        if col in df.columns:
            before = int(df[col].isna().sum())
            df[col] = df.groupby("City", group_keys=False)[col].transform(
                lambda s: interpolate_only_short_gaps(s, max_gap=7)
            )
            interpolated_counts[col] = before - int(df[col].isna().sum())
    df["AQI_Bucket"] = df["AQI"].apply(aqi_bucket)
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Month_Name"] = df["Date"].dt.strftime("%b")
    df["Season"] = df["Month"].map(
        lambda m: "Winter" if m in [12, 1, 2] else
        "Summer" if m in [3, 4, 5] else
        "Monsoon" if m in [6, 7, 8, 9] else "Post-monsoon"
    )
    df["Season"] = pd.Categorical(
        df["Season"], categories=["Winter", "Summer", "Monsoon", "Post-monsoon"], ordered=True
    )
    df.to_csv(OUT / "cleaned_city_day.csv", index=False)
    log = {
        "source_rows_after_valid_city_date": int(before_duplicates),
        "duplicate_city_date_rows_removed": int(duplicate_rows_removed),
        "cleaned_rows": int(len(df)),
        "cities": int(df["City"].nunique()),
        "date_start": str(df["Date"].min().date()),
        "date_end": str(df["Date"].max().date()),
        "negative_values_set_missing": "Negative values in available pollutant columns and AQI were converted to missing.",
        "interpolated_cells_by_pollutant": interpolated_counts,
        "note": "AQI_Bucket is re-labelled from the dataset's existing AQI values; AQI itself is not recalculated from pollutant sub-indices."
    }
    (OUT / "cleaning_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    return df

def save_fig(fig, filename):
    fig.write_html(FIG / filename, include_plotlyjs="cdn", full_html=True)

def run_analysis():
    df = load_and_clean()
    # Basic coverage and headline statistics
    city_aqi = df.groupby("City", observed=True)["AQI"].mean().dropna().sort_values(ascending=False)
    top10 = city_aqi.head(10).rename("Mean AQI").reset_index()
    fig = px.bar(top10, x="City", y="Mean AQI", title="Top 10 Cities by Mean AQI",
                 color="Mean AQI", hover_data={"Mean AQI":":.1f"})
    fig.update_layout(xaxis_tickangle=-35)
    save_fig(fig, "top10_mean_aqi.html")

    # Five worst cities by overall mean AQI; annual PM2.5 averages.
    worst5 = city_aqi.head(5).index.tolist()
    annual_pm = df[df["City"].isin(worst5)].groupby(["Year","City"], observed=True)["PM2.5"].mean().reset_index()
    fig = px.line(annual_pm, x="Year", y="PM2.5", color="City", markers=True,
                  title="Yearly Mean PM2.5: Five Cities with Highest Mean AQI")
    fig.update_layout(yaxis_title="Mean PM2.5 (dataset units)")
    save_fig(fig, "yearly_pm25_worst5.html")

    monthly = df.groupby(["City","Month"], observed=True)["PM2.5"].mean().reset_index()
    pivot = monthly.pivot(index="City", columns="Month", values="PM2.5")
    month_labels = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    pivot = pivot.rename(columns=month_labels)
    ordered_months = [month_labels[m] for m in range(1,13) if month_labels[m] in pivot.columns]
    pivot = pivot[ordered_months]
    fig = px.imshow(pivot, aspect="auto", color_continuous_scale="YlOrRd",
                    labels=dict(x="Month", y="City", color="Mean PM2.5"),
                    title="Monthly Mean PM2.5 by City")
    save_fig(fig, "city_month_pm25_heatmap.html")

    aqicount = df.dropna(subset=["AQI_Bucket"]).groupby(["Year","AQI_Bucket"], observed=True).size().rename("Days").reset_index()
    totals = aqicount.groupby("Year")["Days"].transform("sum")
    aqicount["Percent of observed city-days"] = aqicount["Days"] / totals * 100
    fig = px.bar(aqicount, x="Year", y="Percent of observed city-days", color="AQI_Bucket",
                 category_orders={"AQI_Bucket":AQI_ORDER}, barmode="stack",
                 title="AQI Category Share by Year")
    save_fig(fig, "aqi_category_share.html")

    cols = [c for c in CORR_COLS if c in df.columns]
    corr = df[cols].corr(method="spearman", min_periods=10)
    fig = px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdBu_r",
                    title="Spearman Correlation of Pollutants and AQI")
    save_fig(fig, "spearman_correlation.html")
    corr.to_csv(OUT / "spearman_correlation.csv")

    # Lockdown comparison: use same dates in both years, only where both years exist.
    # Dataset ends on 10-Apr-2020, so this is a partial-overlap comparison, not full lockdown.
    lockdown_start = "03-25"
    lockdown_end = "06-30"
    df["MonthDay"] = df["Date"].dt.strftime("%m-%d")
    candidate = df[(df["Year"].isin([2019, 2020])) &
                   (df["MonthDay"] >= lockdown_start) & (df["MonthDay"] <= lockdown_end)]
    # Keep city only when both years have at least one PM2.5 value in the available comparison window.
    lockdown = candidate.groupby(["City","Year"])["PM2.5"].mean().unstack("Year")
    if 2019 in lockdown.columns and 2020 in lockdown.columns:
        lockdown = lockdown.dropna(subset=[2019, 2020])
        lockdown["Percent change 2020 vs 2019"] = (lockdown[2020] - lockdown[2019]) / lockdown[2019].replace(0, np.nan) * 100
        lockdown = lockdown.reset_index()
    else:
        lockdown = pd.DataFrame(columns=["City",2019,2020,"Percent change 2020 vs 2019"])
    lockdown.to_csv(OUT / "lockdown_city_comparison.csv", index=False)
    if not lockdown.empty:
        fig = px.bar(lockdown.sort_values("Percent change 2020 vs 2019"),
                     x="City", y="Percent change 2020 vs 2019",
                     title="PM2.5 Change: Available Lockdown Dates in 2020 vs Same Dates in 2019",
                     color="Percent change 2020 vs 2019", color_continuous_scale="RdYlGn_r")
        fig.add_hline(y=0, line_dash="dash")
        fig.update_layout(xaxis_tickangle=-35)
        save_fig(fig, "lockdown_pm25_change.html")

    # Health data: World Bank indicator; usually only 2019 has values in supplied export.
    health_path = DATA / "health.csv"
    health_df = pd.DataFrame()
    if health_path.exists():
        health_df = pd.read_csv(health_path)
        if "Country Name" in health_df.columns:
            h_long = health_df.melt(id_vars=[c for c in ["Country Name","Country Code","Indicator Name","Indicator Code"] if c in health_df.columns],
                                    value_vars=[c for c in ["2015","2016","2017","2018","2019","2020"] if c in health_df.columns],
                                    var_name="Year", value_name="Death rate per 100,000")
            h_long["Year"] = pd.to_numeric(h_long["Year"], errors="coerce")
            h_long["Death rate per 100,000"] = pd.to_numeric(h_long["Death rate per 100,000"], errors="coerce")
            h_long = h_long[h_long["Country Name"].isin(COUNTRY_NAMES)].dropna(subset=["Death rate per 100,000"])
            h_long.to_csv(OUT / "health_death_rate_long.csv", index=False)
            if not h_long.empty:
                fig = px.line(h_long, x="Year", y="Death rate per 100,000", color="Country Name", markers=True,
                              title="Age-standardized Mortality Attributed to Household and Ambient Air Pollution")
                save_fig(fig, "health_death_rate.html")
                fig2 = px.bar(h_long[h_long["Year"] == h_long["Year"].max()].sort_values("Death rate per 100,000", ascending=False),
                              x="Country Name", y="Death rate per 100,000",
                              title=f"Country Comparison in Latest Available Year ({int(h_long['Year'].max())})")
                fig2.update_layout(xaxis_tickangle=-30)
                save_fig(fig2, "health_country_comparison.html")
        else:
            h_long = pd.DataFrame()
    else:
        h_long = pd.DataFrame()

    # Scatter plot only when India health and pollution have >= 3 matching years.
    india_pm = df[df["City"].notna()].groupby("Year")["PM2.5"].mean().rename("India city-mean PM2.5").reset_index()
    if not h_long.empty:
        india_health = h_long[h_long["Country Name"] == "India"][["Year","Death rate per 100,000"]]
        matched = india_pm.merge(india_health, on="Year", how="inner").dropna()
        if len(matched) >= 3:
            fig = px.scatter(matched, x="India city-mean PM2.5", y="Death rate per 100,000",
                             trendline="ols", hover_data=["Year"], title="India: Annual City-Mean PM2.5 vs Air-pollution Death Rate")
            save_fig(fig, "india_pm25_vs_death_rate.html")
        else:
            matched.to_csv(OUT / "india_health_pm25_matched_years.csv", index=False)
    else:
        matched = pd.DataFrame()

    # Data-quality outputs: missingness after cleaning and AQI values outside the usual 0-500 scale.
    quality_cols = [c for c in POLLUTANTS + ["AQI"] if c in df.columns]
    missingness = pd.DataFrame({
        "Column": quality_cols,
        "Missing rows": [int(df[c].isna().sum()) for c in quality_cols],
        "Missing (%)": [round(float(df[c].isna().mean() * 100), 2) for c in quality_cols],
        "Valid rows": [int(df[c].notna().sum()) for c in quality_cols],
    }).sort_values("Missing (%)", ascending=False)
    missingness.to_csv(OUT / "missingness_summary.csv", index=False)
    aqi_outliers = df[df["AQI"].notna() & ((df["AQI"] < 0) | (df["AQI"] > 500))]
    aqi_outliers[["City", "Date", "AQI", "AQI_Bucket"]].to_csv(OUT / "aqi_out_of_range_records.csv", index=False)

    # Results summary: numbers computed from actual supplied files.
    season_pm = df.groupby("Season", observed=True)["PM2.5"].mean().dropna().sort_values(ascending=False)
    aqis = df["AQI"].dropna()
    poor_share = (df["AQI_Bucket"].isin(["Poor","Very Poor","Severe"]).sum() / df["AQI_Bucket"].notna().sum() * 100) if df["AQI_Bucket"].notna().any() else np.nan
    yearly_pm = df.groupby("Year")["PM2.5"].mean().dropna()
    driver = corr.loc["AQI"].drop("AQI", errors="ignore").abs().sort_values(ascending=False) if "AQI" in corr.index else pd.Series(dtype=float)
    latest_health_year = int(h_long["Year"].max()) if not h_long.empty else None
    health_latest = h_long[h_long["Year"] == latest_health_year].sort_values("Death rate per 100,000", ascending=False) if latest_health_year else pd.DataFrame()
    summary = {
        "rows_after_cleaning": int(len(df)),
        "city_count": int(df["City"].nunique()),
        "date_start": str(df["Date"].min().date()),
        "date_end": str(df["Date"].max().date()),
        "mean_aqi_all_city_days": round(float(aqis.mean()), 2) if len(aqis) else None,
        "top10_mean_aqi_cities": [{"city": str(i), "mean_aqi": round(float(v),2)} for i,v in city_aqi.head(10).items()],
        "worst_city_by_mean_aqi": str(city_aqi.index[0]) if len(city_aqi) else None,
        "worst_city_mean_aqi": round(float(city_aqi.iloc[0]),2) if len(city_aqi) else None,
        "worst_season_by_pm25": str(season_pm.index[0]) if len(season_pm) else None,
        "season_pm25_means": {str(k): round(float(v),2) for k,v in season_pm.items()},
        "yearly_mean_pm25": {str(k): round(float(v),2) for k,v in yearly_pm.items()},
        "percent_observed_days_poor_or_worse": round(float(poor_share),2) if pd.notna(poor_share) else None,
        "missingness_by_column": {str(row["Column"]): {"missing_rows": int(row["Missing rows"]), "missing_percent": float(row["Missing (%)"])} for _, row in missingness.iterrows()},
        "aqi_values_above_500_count": int((df["AQI"] > 500).sum()),
        "strongest_absolute_spearman_association_with_aqi": {"pollutant": str(driver.index[0]), "rho": round(float(corr.loc["AQI",driver.index[0]]),3)} if len(driver) else None,
        "lockdown_comparison": {
            "requested_period": "25 March–30 June",
            "available_2020_data_end": str(df.loc[df["Year"]==2020,"Date"].max().date()) if (df["Year"]==2020).any() else None,
            "actual_comparison_note": "The supplied city_day.csv ends on 10 April 2020. Comparison is restricted to overlapping dates 25 March–10 April for 2019 and 2020; it cannot represent the full lockdown period.",
            "city_results": lockdown[["City","Percent change 2020 vs 2019"]].round(2).to_dict("records") if not lockdown.empty else [],
            "mean_city_percent_change": round(float(lockdown["Percent change 2020 vs 2019"].mean()),2) if not lockdown.empty else None
        },
        "health_latest_available_year": latest_health_year,
        "health_latest_country_rates": [{"country": str(r["Country Name"]), "rate": round(float(r["Death rate per 100,000"]),1)} for _,r in health_latest.iterrows()] if not health_latest.empty else [],
        "health_years_available": sorted([int(x) for x in h_long["Year"].dropna().unique()]) if not h_long.empty else [],
        "health_scatter_year_count": int(len(matched)) if isinstance(matched, pd.DataFrame) else 0,
        "interpretation_caution": "Associations are descriptive and do not establish causality. 2020 is partial-year data."
    }
    (OUT / "results_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary

if __name__ == "__main__":
    run_analysis()
