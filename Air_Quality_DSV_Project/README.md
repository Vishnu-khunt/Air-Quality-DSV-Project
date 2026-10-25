

### Health data coverage note
The bundled World Bank mortality export has selected-country values for 2019 only. The Health impact dashboard therefore keeps that mortality comparison to 2019. For a real multi-year context, the dashboard separately queries World Bank indicator `EN.ATM.PM25.MC.ZS` (population exposed to PM2.5 above the WHO guideline) when an internet connection is available. This is an exposure indicator, not a death rate. If the API is unavailable, the dashboard shows a warning and the bundled 2019 comparison still works.


Additional multi-year exposure context: World Bank indicator EN.ATM.PM25.MC.M3 (PM2.5 air pollution, mean annual exposure in micrograms per cubic meter): https://data.worldbank.org/indicator/EN.ATM.PM25.MC.M3. This is an exposure measure, not mortality.
