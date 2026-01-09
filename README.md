# Food Price Inflation Analysis in Turkey (2019-2024)

**DSA 210 - Introduction to Data Science Term Project**
**Student:** Işık Giray Önal 34088

---

## Overview

This project analyzes monthly food price changes in Turkey and the relationship between these trends
and USD/TRY exchange rate movements. A composite Food Price Index (base=100 at 2019-01) is computed
from bread, milk, and meat prices, then used for exploratory analysis, hypothesis testing, and
time-series regression.

---

## Data Source and Scope

- **Dataset:** `data/food_inflation_data.csv`
- **Coverage:** 2019-01 to 2024-12 (monthly)
- **Columns:** `Date`, `USD_TRY`, and either `Bread_Price`/`Milk_Price`/`Meat_Price` or
  `Bread_Index`/`Milk_Index`/`Meat_Index` (HICP, 2015=100).
- **Derived:** `Food_Price_Index` is the mean of item-level indices (computed from prices or taken
  directly from index series).
- **Note:** The current dataset is generated from public sources (EVDS USD/TRY + FRED HICP).
  If EVDS access fails, use the script below with `--usd-source fred` and cite FRED for USD/TRY.

---

## Methods

- **EDA:** Time-series plots, scatter plots, summary stats.
- **Hypothesis test:** Pearson correlation between `USD_TRY` and `Food_Price_Index`.
  - **H0:** r = 0 (no correlation)
  - **H1:** r > 0 (positive correlation)
- **Machine learning:** Time-aware cross-validation with lag and rolling features.
  - Models: Linear Regression, Ridge, Lasso, Random Forest
  - Metrics: MAE, RMSE, R2

---

## Results (From Current Dataset)

- **Food Price Index:** 153.13 -> 1320.04 (~8.62x increase)
- **USD/TRY:** 5.37 -> 34.90 (~6.50x increase)
- **Correlation:** r = 0.9891, p = 5.26e-60 (reject H0)
- **Best model (CV mean):** Ridge
  - MAE = 37.47, RMSE = 45.15, R2 = -0.025

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

## Reproducibility

```bash
pip install -r requirements.txt
python3 code/fetch_data.py --out data/food_inflation_data.csv  # optional (requires API keys)
python3 code/analysis.py
python3 code/train_models.py
```

Optional: open `code/machine_learning.ipynb` to reproduce the full ML workflow and figures.

---

## Public Data Retrieval (Optional)

This script downloads USD/TRY and HICP food indices for Turkey and writes
`data/food_inflation_data.csv` with `Date`, `USD_TRY`, `Bread_Index`, `Milk_Index`, `Meat_Index`.

```bash
export EVDS_API_KEY=YOUR_EVDS_KEY
export FRED_API_KEY=YOUR_FRED_KEY
python3 code/fetch_data.py --out data/food_inflation_data.csv
```

If EVDS access fails, you can pull USD/TRY from FRED instead:

```bash
export FRED_API_KEY=YOUR_FRED_KEY
python3 code/fetch_data.py --usd-source fred --out data/food_inflation_data.csv
```

Sources and access notes:

- **TCMB EVDS (USD/TRY):** series `TP.DK.USD.A.YTL`, API key required.
  Example: `https://evds2.tcmb.gov.tr/service/evds/series=TP.DK.USD.A.YTL&startDate=01-01-2019&endDate=31-12-2024&type=json&key=YOUR_API_KEY`
- **FRED (USD/TRY, fallback):** `CCUSMA02TRM618N` (monthly average, Turkish lira per USD).
- **FRED (Eurostat HICP):**
  - Bread & Cereals: `CP0111TRM086NEST`
  - Meat: `CP0112TRM086NEST`
  - Milk, Cheese, Eggs: `CP0114TRM086NEST`

Citations:

- **TCMB EVDS**, Central Bank of the Republic of Turkey, Electronic Data Delivery System (EVDS),
  USD/TRY Exchange Rate Series, https://evds2.tcmb.gov.tr (accessed YYYY-MM-DD).
- **Eurostat HICP via FRED**, Federal Reserve Bank of St. Louis, HICP Turkey food series
  (CP0111TRM086NEST, CP0112TRM086NEST, CP0114TRM086NEST), https://fred.stlouisfed.org (accessed YYYY-MM-DD).

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
