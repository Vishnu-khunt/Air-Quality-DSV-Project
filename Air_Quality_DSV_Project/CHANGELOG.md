# Project update log

## Dashboard improvement release
- Added a fifth **Data quality** tab with missing-value counts and percentages.
- Changed the health tab to a single-year country comparison when only 2019 is available; it no longer implies a meaningful time series.
- Improved the lockdown tab with clearer date limitations, a mean city-level change KPI, and count of cities with decreases.
- Made the city-month heatmap show missing values in gray with an explanatory caption.
- Made yearly city PM2.5 comparisons focus on the five highest mean-AQI cities unless cities are selected.
- Preserved missing city-years as chart gaps rather than filling them with zero.
- Sorted displayed records so valid measurements appear before missing rows.
- Added `outputs/missingness_summary.csv` and `outputs/aqi_out_of_range_records.csv`.
- Kept all reported data limitations explicit; no missing values or health years were fabricated.

## Dashboard hotfix — duplicate column error
- Fixed a Streamlit crash when the selected measure is PM2.5.
- The data-table column list now removes duplicate column names before sorting.
- Sorting still puts missing values last and prioritizes the selected measure.
