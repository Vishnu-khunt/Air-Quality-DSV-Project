# Presentation Outline — 10 Slides
## Slide 1 — Title and Team
- Air Quality in Indian Cities (2015–2020)
- Trends, seasonality, lockdown comparison, and health impact
- Student name, enrollment number, course, institution
- Dataset period and tools used
**Chart/visual:** India outline or a small dashboard screenshot.

## Slide 2 — Problem Statement
- Air pollution varies by city, pollutant, and season.
- Large datasets are difficult to compare without analysis.
- Need to identify patterns and communicate them clearly.
- Health data uses a different geographic scale than city pollution data.
**Chart/visual:** Simple project workflow diagram.

## Slide 3 — Objectives
- Rank cities using mean AQI.
- Analyze yearly and seasonal PM2.5 patterns.
- Compare available lockdown dates in 2020 with the same dates in 2019.
- Compare air-pollution mortality rates across eight countries.
**Chart/visual:** Four objective icons or four KPI tiles.

## Slide 4 — Dataset Description
- Primary file: city_day.csv.
- 25,555 rows, 22 cities, 2015-01-01 to 2020-04-10 in the supplied file.
- Pollutants include PM2.5, PM10, NO2, SO2, CO, and O3.
- Health file: World Bank age-standardized mortality indicator.
**Chart/visual:** Dataset profile table or coverage timeline.

## Slide 5 — Data Cleaning and Preparation
- Remove duplicate City-Date rows.
- Convert negative readings to missing values.
- Interpolate only internal gaps of up to seven consecutive records.
- Derive Year, Month, Season, and AQI category labels.
- Measure missingness and flag AQI values outside the usual scale.
**Chart/visual:** Before/after cleaning flowchart or missingness bar chart.

## Slide 6 — City Ranking and Trends
- Show the ten cities with highest mean AQI.
- Compare yearly PM2.5 for the five highest-AQI cities.
- Discuss observed patterns from actual analysis outputs.
- Treat 2020 as partial-year data.
**Chart/visual:** `top10_mean_aqi.html` and/or `yearly_pm25_worst5.html`.

## Slide 7 — Seasonality and AQI Categories
- Compare winter, summer, monsoon, and post-monsoon PM2.5.
- Use the city-month heatmap to identify local patterns.
- Show the percentage distribution of AQI categories by year.
- Explain possible weather mechanisms without assuming they apply everywhere.
**Chart/visual:** City-month heatmap and AQI category stacked bar.

## Slide 8 — Lockdown and Correlation
- Compare 25 March–10 April in 2019 and 2020, the only overlapping period available.
- Explain the percentage-change formula.
- Present the Spearman correlation heatmap.
- Avoid claiming that lockdown alone caused observed changes.
**Chart/visual:** Lockdown percentage-change bar chart and correlation heatmap.

## Slide 9 — Health Impact and Limitations
- Compare the available 2019 mortality rates for eight countries.
- Explain that rates are age-standardized per 100,000 population.
- Supplied health data does not support a multi-year trendline.
- Correlation and national mortality comparisons do not prove city-level causation.
**Chart/visual:** `health_country_comparison.html`.

## Slide 10 — Conclusion and Recommendations
- Summarize the strongest data-backed findings.
- Recommend winter preparedness and evidence-based source controls.
- Recommend transport and industrial emission controls where locally supported.
- Future work: longer data coverage, weather variables, and compatible health data.
**Chart/visual:** Dashboard screenshot plus 3 recommendations.
