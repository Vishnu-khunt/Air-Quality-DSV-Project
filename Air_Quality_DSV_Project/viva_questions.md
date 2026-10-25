# Viva Preparation: 15 Likely Questions and Short Answers

1. **What is AQI?**  
   AQI means Air Quality Index. It converts air-pollution measurements into a scale that communicates how clean or polluted the air is.

2. **What is PM2.5?**  
   PM2.5 is particulate matter with an aerodynamic diameter of 2.5 micrometres or less. These fine particles can penetrate deep into the lungs and are associated with serious health risks.

3. **Why is PM2.5 dangerous?**  
   Its small size allows it to reach deep parts of the respiratory system. Long-term exposure is associated with cardiovascular and respiratory illness.

4. **Why did you remove duplicate City-Date rows?**  
   Duplicate rows can give a city-date extra weight and distort averages. The project keeps one record for each city and date.

5. **Why convert negative readings to missing values instead of zero?**  
   Negative concentration readings are invalid. Zero would falsely indicate that no pollutant was measured, so missing values are more honest.

6. **Why interpolate missing values?**  
   Short internal gaps can be estimated from nearby observations to reduce gaps in trend analysis. Interpolation is limited to seven consecutive records and is not used for long or edge gaps.

7. **What is a limitation of interpolation?**  
   It estimates values rather than measuring them and can smooth real pollution spikes. The project logs the number of interpolated cells.

8. **Why use seasonal analysis?**  
   Pollution can vary with weather, rainfall, atmospheric mixing, and seasonal human activity. Grouping months into seasons helps compare these patterns.

9. **Why might monsoon PM2.5 be lower?**  
   Rain can remove particles from the atmosphere, and weather patterns may improve dispersion. This is a possible explanation, not a guaranteed result for every city or year.

10. **Why use Spearman correlation instead of only Pearson correlation?**  
    Spearman measures monotonic relationships using ranks and does not require a linear relationship. It can be useful when data are skewed or contain outliers.

11. **Does a high correlation prove that a pollutant causes a high AQI?**  
    No. Correlation measures association, not causation. AQI is also constructed from pollutant sub-indices, so some association is expected.

12. **How did you calculate percentage change during the lockdown comparison?**  
    `(2020 mean − 2019 mean) / 2019 mean × 100`. A negative value indicates a decrease in the 2020 comparison period.

13. **Why is your lockdown result incomplete?**  
    The supplied city-day file ends on 10 April 2020. Therefore, the code compares only 25 March–10 April with the same dates in 2019, not the entire period through 30 June.

14. **What does age-standardized mortality per 100,000 mean?**  
    It is a population rate adjusted to a standard age structure so that age differences between populations are less likely to distort comparisons. It is not a raw death count.

15. **What is the role of Streamlit in your project?**  
    Streamlit turns the Python analysis into an interactive web dashboard with filters, KPI cards, charts, and separate analysis tabs without requiring a complex frontend.
