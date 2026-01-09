# Food Price Inflation Analysis in Turkey (2019-2024)

**DSA 210 - Introduction to Data Science Term Project**
**Student:** Işık Giray Önal 34088

---

## Overview

This project studies monthly food price movements in Turkey and their relationship with USD/TRY
exchange rates. A composite Food Price Index is constructed from bread, milk, and meat series and
used for EDA, hypothesis testing, and time-series regression.

---

## Data and Sources

**Dataset:** `data/food_inflation_data.csv` (2019-01 to 2024-12, monthly)

**Columns**
- `Date`
- `USD_TRY`
- Food item series as either:
  - `Bread_Price`, `Milk_Price`, `Meat_Price`, or
  - `Bread_Index`, `Milk_Index`, `Meat_Index` (HICP, 2015=100)

**Derived**
- `Food_Price_Index`: mean of item-level indices. If price columns are used, indices are computed
  with the first month as base.

**Primary sources**
- **TCMB EVDS (USD/TRY):** `TP.DK.USD.A.YTL` (monthly, API key required)
- **Eurostat HICP via FRED (food indices):**
  - Bread & Cereals: `CP0111TRM086NEST`
  - Meat: `CP0112TRM086NEST`
  - Milk, Cheese, Eggs: `CP0114TRM086NEST`

**Fallback for USD/TRY**
- **FRED (USD/TRY):** `CCUSMA02TRM618N` (monthly average)

**Notes**
- HICP series are indices, not item-level price observations.
- If EVDS access fails, you can use the FRED USD/TRY fallback.

---

## Methods

- **EDA:** Time-series plots, scatter plots, summary statistics
- **Hypothesis test:** Pearson correlation between `USD_TRY` and `Food_Price_Index`
- **Machine learning:** Time-aware cross-validation with lag and rolling features
  - Models: Linear Regression, Ridge, Lasso, Random Forest
  - Metrics: MAE, RMSE, R2

---

## Results (Current Dataset)

- **Food Price Index:** 153.13 -> 1320.04 (~8.62x increase)
- **USD/TRY:** 5.37 -> 34.90 (~6.50x increase)
- **Correlation:** r = 0.9891, p = 5.26e-60 (reject H0)
- **Best model (CV mean):** Ridge
  - MAE = 37.47, RMSE = 45.15, R2 = -0.025

---

## Reproducibility

```bash
pip install -r requirements.txt
python3 code/analysis.py
python3 code/train_models.py
```

Optional: open `code/machine_learning.ipynb` to reproduce the full ML workflow and figures.

---

## Public Data Retrieval (Optional)

The script below pulls USD/TRY from EVDS and food indices from FRED, then writes
`data/food_inflation_data.csv`.

```bash
export EVDS_API_KEY=YOUR_EVDS_KEY
export FRED_API_KEY=YOUR_FRED_KEY
python3 code/fetch_data.py --usd-source evds --out data/food_inflation_data.csv
```

If EVDS access fails, use the USD/TRY fallback from FRED:

```bash
export FRED_API_KEY=YOUR_FRED_KEY
python3 code/fetch_data.py --usd-source fred --out data/food_inflation_data.csv
```

**Citations**
- **TCMB EVDS**, Central Bank of the Republic of Turkey, Electronic Data Delivery System (EVDS),
  USD/TRY Exchange Rate Series, https://evds2.tcmb.gov.tr (accessed YYYY-MM-DD).
- **Eurostat HICP via FRED**, Federal Reserve Bank of St. Louis, HICP Turkey food series
  (CP0111TRM086NEST, CP0112TRM086NEST, CP0114TRM086NEST), https://fred.stlouisfed.org
  (accessed YYYY-MM-DD).

---

## Project Structure

```
.
├── data/
│   ├── food_inflation_data.csv
│   ├── metrics.csv
│   └── predictions.csv
├── code/
│   ├── analysis.py
│   ├── fetch_data.py
│   ├── train_models.py
│   ├── ml_pipeline.py
│   └── machine_learning.ipynb
├── images/
│   ├── Figure_1.png
│   ├── Figure_2.png
│   └── prediction_plot.png
├── README.md
└── requirements.txt
```

---

## Limitations and Future Work

- Public HICP series are indices, not item-level price observations.
- Limited food items and a short time range.
- Add official sources (TUIK/TCMB) and more macro indicators (CPI, wage index, energy costs).
- Compare additional time-series models (SARIMAX, Prophet) and validate on newer data.

---

## AI Assistance Disclosure

- **Prompt:** "kanka bugün 9 ocak projeyi bitirsene"
- **Output:** Updated analysis scripts, aligned ML pipeline to the current dataset, regenerated
  figures/metrics, and revised this README for final submission.
- **Prompt:** "proje dökümanında bişey demiyorsa keyfine göre"
- **Output:** Added public-data retrieval guidance, a fetch script, and updated documentation.
- **Prompt:** "EVDS and FRED API keys provided"
- **Output:** Added EVDS header support, monthly aggregation, and refreshed results/figures.
