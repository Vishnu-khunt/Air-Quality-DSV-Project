# Air Quality Analysis and Data Visualization

An interactive Data Science and Visualization project exploring air
quality patterns across Indian cities, with supporting data-quality
analysis, visualizations, and selected health-indicator comparisons.

## Project Overview

This project analyzes city-level air-quality observations from
2015--2020. It uses Python for data cleaning and analysis, and an
interactive Streamlit dashboard to explore pollution trends, seasonal
patterns, the available lockdown-period comparison, and selected
health-related indicators.

## Features

-   Explore air-quality trends across cities and years.
-   Compare pollutants such as PM2.5, PM10, NO2, CO, SO2, O3, and AQI
    when available in the dataset.
-   Examine seasonal patterns and monthly PM2.5 variation.
-   Review data-quality outputs, including missingness and records with
    out-of-range AQI values.
-   Explore the available lockdown-period comparison.
-   View interactive Plotly charts saved as HTML files.
-   Review the bundled health comparison with its available data
    coverage clearly noted.

## Technology Stack

-   **Python**
-   **Pandas** and **NumPy** for data processing
-   **Plotly** for interactive charts
-   **Streamlit** for the dashboard
-   **Statsmodels** for statistical analysis
-   **Requests** for optional World Bank indicator access

## Project Structure

``` text
Air_Quality_DSV_Project/
├── app.py
├── analysis.py
├── requirements.txt
├── README.md
├── report.md
├── presentation_outline.md
├── viva_questions.md
├── CHANGELOG.md
├── data/
│   ├── city_day.csv
│   └── health.csv
├── notebooks/
│   └── README.md
└── outputs/
    ├── cleaned_city_day.csv
    ├── results_summary.json
    ├── key_findings.csv
    ├── data-quality and analysis CSV/JSON files
    └── figures/
        └── interactive HTML charts
```

## Getting Started

### 1. Install Python

Install a recent version of Python (Python 3.10 or newer is
recommended).

### 2. Open the project folder

Open PowerShell or Command Prompt in the `Air_Quality_DSV_Project`
directory.

### 3. Create and activate a virtual environment (recommended)

**Windows PowerShell:**

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt instead:

``` bat
.venv\Scripts\activate.bat
```

### 4. Install dependencies

``` powershell
python -m pip install -r requirements.txt
```

### 5. Run the analysis (if you want to regenerate the outputs)

``` powershell
python analysis.py
```

### 6. Launch the dashboard

``` powershell
python -m streamlit run app.py
```

Streamlit will display a local URL in the terminal, usually
`http://localhost:8501`. Open it in your browser.

The dashboard uses generated files under `outputs/`. Run `analysis.py`
first if the cleaned dataset or summary outputs are missing.

## Explore the Visualizations

Interactive HTML charts are stored in `outputs/figures/`. Open any
`.html` file in a web browser to explore it.

## Data Notes and Limitations

-   The project includes a city-level air-quality dataset and a bundled
    health-indicator export. Check the dataset source and its
    documentation before reusing or redistributing the data.
-   The bundled health mortality data contains selected-country values
    for 2019 only. The dashboard therefore limits that mortality
    comparison to the available year.
-   When an internet connection is available, the dashboard separately
    queries a World Bank PM2.5 exposure indicator for additional
    context. Exposure is not the same as mortality, and the two measures
    should not be interpreted interchangeably.
-   Results depend on the coverage, quality, and limitations of the
    underlying datasets. Observed associations do not by themselves
    prove causation.

## Main Files

-   `analysis.py` --- data cleaning, analysis, and output generation.
-   `app.py` --- interactive Streamlit dashboard.
-   `requirements.txt` --- Python package dependencies.
-   `report.md` --- project report.
-   `presentation_outline.md` --- presentation outline.
-   `viva_questions.md` --- project viva preparation.
-   `outputs/figures/` --- saved interactive charts.

## Running the Project

From the project directory:

``` powershell
python -m pip install -r requirements.txt
python analysis.py
python -m streamlit run app.py
```

## Author

Add your name, course, department, and institution here before
submission if required by your instructor.

## License

No license has been specified yet. Unless a license is added, others do
not automatically receive permission to reuse this project's code.
