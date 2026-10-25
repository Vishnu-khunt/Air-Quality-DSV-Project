# Air Quality in Indian Cities (2015–2020): Trends, Seasonality, COVID-19 Lockdown Effect and Health Impact
**Data Science and Visualization Project Report**

**Student:** ____________________  
**Enrollment number:** ____________________  
**Course / Semester:** Data Science and Visualization, Semester VII  
**Institution:** A. D. Patel Institute of Technology  
**Academic year:** 2026–27

> **How to finalize this report:** Run `python analysis.py`. Use `outputs/results_summary.json`, `outputs/cleaning_log.json`, and the exported CSV files to fill in the bracketed result fields. The report does not invent results. Some analyses are explicitly limited by the coverage of the supplied files.

## Abstract
Air pollution is an important environmental and public-health issue. Fine particulate matter (PM2.5), larger particulate matter (PM10), nitrogen dioxide (NO2), sulphur dioxide (SO2), carbon monoxide (CO), and ozone (O3) are among the pollutants monitored in urban air. This project applies data cleaning, exploratory data analysis, statistical summaries, and interactive visualization to daily air-quality observations from Indian cities between 2015 and 2020. The main questions concern the most polluted cities, changes in PM2.5 over time, seasonal variation, the pollution change during the available part of the 2020 COVID-19 lockdown compared with the same dates in 2019, and cross-country differences in air-pollution mortality.

The primary dataset is the Kaggle `city_day.csv` file. The health dataset is a World Bank indicator on age-standardized mortality attributed to household and ambient air pollution. Python, Pandas, NumPy, Plotly, and Streamlit are used to clean, analyze, and visualize the data. Duplicate city-date records are removed, negative measurements are treated as missing, short internal pollutant gaps are interpolated, and AQI category labels are assigned from the existing AQI values. The analysis creates city rankings, yearly trends, seasonal heatmaps, AQI category shares, Spearman correlations, a matched-date lockdown comparison, and a country mortality comparison.

The supplied air-quality file ends on 10 April 2020, so it cannot evaluate the entire 25 March–30 June lockdown window. The supplied health export has the requested countries' mortality values for 2019 only, limiting the health comparison to that year. These limitations are documented rather than concealed. The project demonstrates a reproducible workflow for environmental data analysis and emphasizes that descriptive correlations do not prove causation.

## 1. Introduction
Air quality affects daily life, urban planning, transport policy, industrial regulation, and public health. Pollution levels can vary by location, time of year, weather, and human activity. Cities with dense traffic, industrial activity, construction, or regional pollution sources may experience high pollutant concentrations. Seasonal weather also influences pollution: cooler conditions and lower atmospheric mixing can trap pollutants near the ground, while rainfall can remove some particles from the air. However, seasonal patterns differ by location and pollutant, so they should be measured from data rather than assumed.

Data science offers tools for organizing large datasets, identifying patterns, comparing groups, and communicating findings. Visualization is particularly useful because a line chart can show a trend, a heatmap can expose monthly patterns, and a correlation matrix can summarize associations between measured variables. An interactive dashboard makes these findings accessible to a user who wants to select a city, year, season, or pollutant.

This project uses city-day air-quality data for India and a separate international mortality indicator. It combines numerical summaries with visual exploration while keeping the interpretation within the limits of the available observations.

## 2. Problem Statement and Objectives
### Problem statement
Air-quality datasets contain many cities, dates, pollutants, and missing values. Without a consistent cleaning process and suitable visualizations, it is difficult to compare cities, understand seasonal changes, or communicate the scale of pollution. A further challenge is connecting local pollutant measurements with national health indicators that may use different years, units, and geographic scales.

### Objectives
1. Identify the cities with the highest mean AQI and examine yearly PM2.5 changes.
2. Measure seasonal PM2.5 differences across winter, summer, monsoon, and post-monsoon periods.
3. Compare PM2.5 during the available portion of the 2020 lockdown with the same calendar dates in 2019.
4. Compare the latest available air-pollution mortality indicator for India and seven other countries.
5. Build an interactive Streamlit dashboard and provide a reproducible analysis pipeline.

## 3. Dataset Description
### 3.1 Primary air-quality dataset
The primary file, `city_day.csv`, contains daily city-level observations with columns for City, Date, PM2.5, PM10, NO, NO2, NOx, NH3, CO, SO2, O3, Benzene, Toluene, Xylene, AQI, and AQI_Bucket. The supplied file contains **25,555 rows and 22 cities**, covering **1 January 2015 to 10 April 2020** before project cleaning. The exact cleaned row count and any removed duplicate count are written to `outputs/cleaning_log.json`.

The values represent reported city-day measurements in the supplied dataset. Pollutant units should be interpreted according to the dataset documentation; the project does not combine unlike pollutant units into a single concentration measure. AQI is a composite index and is treated separately from individual pollutant concentrations.

### 3.2 Health dataset
The optional health file is derived from the World Bank indicator `SH.STA.AIRP.P5`: “Mortality rate attributed to household and ambient air pollution, age-standardized (per 100,000 population).” It includes India, China, Pakistan, Bangladesh, Nepal, the United States, the United Kingdom, and Brazil. In the supplied export, these selected countries have a non-missing value for 2019, while the other years requested for a trend are missing. Therefore, the supported comparison is a cross-country comparison for 2019 only. This mortality indicator is not a direct count of deaths and is not a city-specific outcome.

### 3.3 Data limitations identified before analysis
- The air-quality file ends on 10 April 2020; the requested period through 30 June 2020 is unavailable.
- The health export does not contain a multi-year mortality series for the selected countries. The dashboard retrieves a separate World Bank multi-year PM2.5 exposure indicator when an internet connection is available; this cannot be interpreted as deaths or compared directly with city-day concentration values.
- The air-quality dataset covers 22 cities and should not be described as a complete census of every Indian city.
- Missing measurements and monitoring coverage may affect comparisons across cities and years.

## 4. Methodology
### 4.1 Tools
Python is used as the main programming language. Pandas handles tabular data and group-by operations; NumPy supports numerical calculations and interpolation; Plotly produces interactive charts; and Streamlit presents the results in a browser-based dashboard. Statsmodels is included in the environment for optional statistical extensions, although the core project does not require a complex predictive model.

### 4.2 Data cleaning
**Date parsing:** The Date field is converted to a datetime type. Rows without a valid city or date are removed because they cannot be assigned to a city-date time series.

**Duplicate removal:** Duplicate City-Date records are removed, keeping the first occurrence. The combination of city and date is intended to identify one daily observation per city.

**Negative values:** Negative pollutant readings are physically invalid for these concentration measures. They are converted to missing values instead of being replaced with zero, because zero would incorrectly imply no pollution. Negative AQI values are also set to missing.

**Missing-value interpolation:** For each city and pollutant, internal missing runs are examined. Linear interpolation is applied only when the entire consecutive missing run is no longer than seven records and there are valid values on both sides. Longer gaps and leading or trailing gaps remain missing. This reduces small gaps while avoiding unsupported extrapolation. The supplied data is city-day data; missing calendar dates that have no row are not automatically created by this operation.

**AQI category labels:** The existing AQI value is mapped to the project's requested bands: Good (0–50), Satisfactory (51–100), Moderate (101–200), Poor (201–300), Very Poor (301–400), and Severe (401+). The project re-labels AQI_Bucket from the existing AQI; it does not independently recalculate AQI from pollutant sub-indices. This distinction matters because official AQI calculation uses pollutant-specific sub-indices and data-availability rules.

**Time features:** Year, Month, month name, and Season are created from Date. Winter is December–February, Summer is March–May, Monsoon is June–September, and Post-monsoon is October–November.

### 4.3 Exploratory analysis
The analysis creates the following visualizations:
1. A bar chart of the ten cities with the highest mean AQI.
2. A yearly line chart of mean PM2.5 for the five cities with the highest overall mean AQI.
3. A city-by-month PM2.5 heatmap.
4. A stacked bar chart showing the percentage of observed city-days in each AQI category by year.
5. A Spearman correlation heatmap for PM2.5, PM10, NO2, SO2, CO, O3, and AQI.
6. A city-level percentage-change chart for PM2.5 over overlapping lockdown-period dates in 2020 compared with 2019.
7. A country comparison of the available World Bank air-pollution mortality values.
8. An India PM2.5 versus mortality scatter plot only if enough matching annual observations exist. The supplied mortality data does not support a multi-year mortality trendline, so the project does not fabricate one. A separate multi-year exposure chart uses World Bank indicator `EN.ATM.PM25.MC.ZS` when the dashboard has internet access.

### 4.4 Lockdown comparison method
For each city, the mean PM2.5 during 25 March–30 June 2019 would ideally be compared with the same dates in 2020. However, the supplied file ends on 10 April 2020. Therefore, the executable analysis compares 25 March–10 April in each year and clearly labels the result as a partial-window comparison. Percentage change is calculated as:

**Percentage change = ((2020 mean − 2019 mean) / 2019 mean) × 100**

A negative result indicates a reduction. The comparison is restricted to cities with observations in both years. This is a descriptive before-versus-year comparison, not proof that lockdown alone caused the change; weather, regional activity, monitoring coverage, and other factors may also contribute.

### 4.6 Data-quality diagnostics
A separate missingness summary reports the number and percentage of missing values for each pollutant and AQI after cleaning. The dashboard includes a Data quality tab with the same information for the current filter selection. City-month heatmap cells without a valid PM2.5 average are displayed in gray and explained as missing data, not zero pollution. Records with AQI values outside the usual 0–500 scale are exported to `outputs/aqi_out_of_range_records.csv` for review rather than silently changing the recorded AQI.

### 4.5 Statistical approach
Means summarize average pollutant levels, while percentages show the composition of AQI categories. Spearman rank correlation is used because it measures monotonic association and does not require a linear relationship or normally distributed variables. Correlations are descriptive and cannot establish causation. The health indicator is age-standardized and national, whereas the pollution data is city-level; this scale mismatch is explicitly recognized.

## 5. Analysis and Results
This section should be finalized after running the project. The code exports the results to `outputs/results_summary.json`, which is the source of truth for numerical findings.

### 5.1 Most polluted cities
The city ranking is based on each city's mean observed AQI over the available data. The generated bar chart is `outputs/figures/top10_mean_aqi.html`. Insert the leading city and its mean AQI from the `worst_city_by_mean_aqi` and `worst_city_mean_aqi` fields in `results_summary.json`. The ranking describes this dataset and its monitoring period; it should not be generalized to every Indian city or every year.

### 5.2 Yearly PM2.5 trend
The yearly means are stored in the `yearly_mean_pm25` field. Use the line chart `yearly_pm25_worst5.html` to compare cities. Treat 2020 as a partial year because observations stop on 10 April. A partial-year mean is not directly comparable with a complete annual mean because later seasons are absent.

### 5.3 Seasonal pattern
The `season_pm25_means` field reports mean PM2.5 by season. The highest season is listed in `worst_season_by_pm25`. Compare all four seasonal means and describe the size of the differences, not just the rank. Seasonal averages can be influenced by the fact that cities have different observation coverage and pollutant sources. Monsoon rainfall may reduce airborne particles, while winter meteorology can favor pollutant accumulation, but the data must determine whether that pattern appears in the selected observations.

### 5.4 AQI category distribution
The stacked chart `aqi_category_share.html` displays the percentage of observed city-days in each category for each year. This percentage is calculated among city-days with a valid AQI value, not among all calendar days in India. Since the number of monitored cities and missing observations may vary, the chart is a dataset-level description.

### 5.5 Pollutant correlations
The correlation matrix is exported to `outputs/spearman_correlation.csv`. The strongest absolute association between AQI and the selected pollutants is recorded in `strongest_absolute_spearman_association_with_aqi`. Report both the pollutant and its Spearman rho. A high association may partly reflect the fact that AQI is derived from pollutant sub-indices; it does not independently prove a causal effect.

### 5.6 COVID lockdown-period comparison
The city-level values are in `outputs/lockdown_city_comparison.csv`. The mean city percentage change is stored in `lockdown_comparison.mean_city_percent_change`. Explain that this result covers only 25 March–10 April because later 2020 data is absent. Do not describe it as a full March–June estimate. A more complete analysis requires an extended source dataset with observations through 30 June 2020.

### 5.7 International health comparison
The World Bank indicator is measured as age-standardized mortality per 100,000 population. The available 2019 rates for the selected countries are listed in `health_latest_country_rates` in the JSON output. Compare these rates for 2019 only. Do not describe them as 2015–2020 trends, and do not infer that a particular city's PM2.5 caused a country's mortality rate. Population structure, household pollution, healthcare, exposure patterns, and the indicator's methodology all affect interpretation.

## 6. Key Insights

The following findings were calculated from the supplied files by running `python analysis.py`.

1. **Highest mean AQI:** Ahmedabad ranked highest in this dataset, with a mean AQI of **473.91**. Delhi was second at **262.26**, followed by Patna at **248.27**.
2. **Seasonality:** Winter had the highest mean PM2.5 at **103.28**, followed by post-monsoon (**94.84**), summer (**65.17**), and monsoon (**40.61**). In this dataset, monsoon mean PM2.5 was about **62.67** lower than winter.
3. **Yearly PM2.5:** Mean PM2.5 was **82.76** in 2015, rose to **95.26** in 2016, and then declined to **60.23** in 2019. The 2020 mean was **61.01**, but it covers only 1 January–10 April and must not be interpreted as a full-year value.
4. **Strongest AQI association:** Among the selected variables, PM10 had the strongest absolute Spearman association with AQI (**rho = 0.872**). This is an association, not proof of causation, and AQI is itself based on pollutant sub-indices.
5. **Available lockdown dates:** Across cities with data in both years, the unweighted mean of city-level PM2.5 percentage changes was **-13.31%** for 25 March–10 April 2020 versus the same dates in 2019. A negative value indicates a decrease. This is not a full 25 March–30 June lockdown estimate.
6. **AQI category share:** **29.62%** of city-day records with a non-missing AQI category were labelled Poor, Very Poor, or Severe using the project's specified category bands.
7. **2019 mortality comparison:** The World Bank indicator was highest among the selected countries in Pakistan (**192.1 deaths per 100,000**), followed by Nepal (**177.9**), Bangladesh (**143.9**), and India (**139.3**). The values are age-standardized mortality rates attributed to household and ambient air pollution, not raw death counts.
8. **Coverage limitation:** The air-quality file contains **25,555 rows across 22 cities** and ends on **2020-04-10**. The health file has selected-country mortality values only for 2019, so it does not support a multi-year mortality trend or a multi-year India PM2.5-versus-mortality trendline. The dashboard separately fetches a multi-year population-exposure indicator from the World Bank API when online; exposure is not mortality.

These results describe the supplied dataset and should be interpreted in light of its coverage, missing observations, and the difference between city-level pollution measurements and national health rates.

## 7. Recommendations
1. **Winter emission controls:** Use local seasonal forecasts and monitoring data to plan temporary controls during high-pollution periods. Focus on sources supported by local emission inventories.
2. **Stubble burning:** Improve crop-residue management support, access to machinery, and monitoring in regions where agricultural burning is a documented contributor. Do not assume that all city pollution originates from nearby farms.
3. **Transport emissions:** Support public transport, vehicle inspection and maintenance, cleaner fuels, and enforcement of applicable emission standards.
4. **Industrial and construction dust controls:** Monitor industrial sources and enforce dust suppression and construction-site practices where measurements and inventories indicate a need.
5. **Early-warning alerts:** Combine measured AQI, weather forecasts, and clear public guidance. Alerts should identify sensitive groups and recommended protective actions.
6. **Data quality:** Improve monitoring continuity, metadata, station coverage, and publication of validated data. Clear data documentation improves public trust and future research.
7. **Health surveillance:** Where permitted and ethically governed, link aggregated health indicators with exposure data at compatible geographic and temporal scales. Use appropriate epidemiological designs before making causal claims.

## 8. Limitations
- The supplied air-quality dataset contains 22 cities and ends on 10 April 2020.
- The full 25 March–30 June 2020 lockdown period cannot be evaluated using this file.
- The supplied World Bank mortality export only provides 2019 values for the eight selected countries. The additional multi-year exposure chart uses a different indicator and requires internet access.
- AQI is re-categorized from the supplied AQI column; official AQI is not recalculated from sub-indices.
- Linear interpolation can smooth real short-term fluctuations and does not replace actual measurements.
- The dataset may contain non-random missingness, different monitoring coverage, and changes in measurement availability.
- A national health mortality rate and city-level pollution mean are not perfectly comparable.
- Correlation is not causation; the project is observational and does not isolate all confounding factors.
- The 2020 observations are partial-year and should not be treated as a complete annual average.

## 9. Conclusion
This project provides a reproducible data-science workflow for examining air quality in Indian cities. It cleans daily observations, derives time and season fields, ranks cities, explores PM2.5 trends, compares seasonal patterns, calculates pollutant correlations, and visualizes a matched-date lockdown-period comparison. A Streamlit dashboard makes the analysis easier to explore through city, year, and pollutant filters.

The project also demonstrates an important principle in data science: analysis must respect the limits of the data. The primary dataset cannot measure the complete lockdown period because it ends on 10 April 2020, and the supplied mortality export does not provide the requested multi-year health series. These gaps are documented so that the report remains honest and reproducible. Future work can use a longer air-quality time series, compatible multi-year mortality data, weather variables, and city-level health indicators to support more robust statistical analysis.

## 10. References
1. Kaggle. *Air Quality Data in India (2015–2020)*, city-day dataset. Dataset supplied for this project; cite the exact Kaggle dataset page used to download the CSV in the final submission.
2. World Bank. *Mortality rate attributed to household and ambient air pollution, age-standardized (per 100,000 population)*, indicator `SH.STA.AIRP.P5`. https://data.worldbank.org/indicator/SH.STA.AIRP.P5
3. Central Pollution Control Board (CPCB), India. National Air Quality Index resources. https://cpcb.nic.in/
4. World Health Organization. Air pollution and health resources. https://www.who.int/health-topics/air-pollution
5. McKinney, W. *Data Structures for Statistical Computing in Python*. Proceedings of the Python in Science Conference, 2010.
6. Plotly Python documentation. https://plotly.com/python/
7. Streamlit documentation. https://docs.streamlit.io/
8. Pandas documentation. https://pandas.pydata.org/docs/

## Appendix: How to reproduce the results
1. Install dependencies using `pip install -r requirements.txt`.
2. Run `python analysis.py`.
3. Open `outputs/results_summary.json` and use the exact generated values in Section 6.
4. Open the interactive charts in `outputs/figures/`.
5. Run `streamlit run app.py` to demonstrate the dashboard.


Additional multi-year exposure context: World Bank indicator EN.ATM.PM25.MC.M3 (PM2.5 air pollution, mean annual exposure in micrograms per cubic meter): https://data.worldbank.org/indicator/EN.ATM.PM25.MC.M3. This is an exposure measure, not mortality.
