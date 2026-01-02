# Food Price Inflation Analysis in Turkey (2019–2025)

**DSA 210 - Introduction to Data Science Term Project**
**Student:** Işık Giray Önal 34088

---

## 📌 Overview

This project analyzes the change in food prices over time in Turkey and explores the relationship between these trends, the inflation rate, and exchange rate fluctuations (USD/TRY).

The primary goal is to visualize the correlation between currency devaluation and food inflation, and eventually build a regression model to predict future prices based on economic indicators.

---

## 📂 Project Structure

The repository is organized as follows:

    dsa210-term-project/
    ├── data/
    │   └── turkey_food_inflation_dataset.csv   # Processed dataset (Currently Synthetic/Test Data)
    ├── code/
    │   └── analysis.ipynb                      # Source code for Data Generation, EDA, and Hypothesis Testing
    ├── images/                                 # Folder for saved visualization exports
    ├── README.md                               # Project documentation
    └── requirements.txt                        # List of Python dependencies

---

## 📊 Data Source & Processing (Nov 28 Milestone Update)

For the current milestone (Nov 28), the project pipeline has been successfully established using a **synthetic dataset** designed to mimic real-world economic trends in Turkey.

- **Current Data:** A generated dataset covering the period from **Jan 2019 to Jan 2025**.
- **Variables:**
  - `Date`: Monthly timestamps.
  - `USD_TRY`: Simulated exchange rate data exhibiting an upward trend with market fluctuations.
  - `Food_Price_Index`: Simulated food price index strongly correlated with currency changes and inflation noise.
- **Next Steps:** This synthetic data serves as a placeholder to validate the analysis code. It will be replaced by real scraped data from **TÜİK (Turkish Statistical Institute)** and **TCMB (Central Bank of Turkey)** for the final submission in January.

---

## 02 Jan Milestone Update — Machine Learning ✅

The machine learning milestone has been completed using the synthetic monthly dataset in `data/`.
A time-respecting train/test split was applied and several regression models were trained to predict
`Food_Price_Index` using `USD_TRY`, time features, and lag/rolling features.

**Baselines**

- Naive baseline (last-month value)

**Models**

- Linear Regression, Ridge, Lasso
- Random Forest Regressor
- HistGradientBoostingRegressor

**Outputs**

- Notebook: `code/machine_learning.ipynb`
- Figures exported to `images/` (actual vs predicted, residuals, feature importance/coefs)

---

## 🔍 Exploratory Data Analysis (EDA) Findings

The initial analysis performed in `analysis.ipynb` yielded the following insights:

1.  **Trend Analysis:** Both the USD/TRY exchange rate and the Food Price Index show a consistent and steep upward trend over the last 6 years.
2.  **Volatility:** Food prices exhibit higher volatility compared to the exchange rate, suggesting that factors beyond currency (e.g., supply chain issues, seasonality) also play a role.
3.  **Visual Correlation:** Time-series plots confirm a parallel movement between currency devaluation and the increase in food prices.

---

## 🧪 Hypothesis Testing

We statistically tested the relationship between currency devaluation and food prices.

- **Hypothesis ($H_1$):** There is a significant positive correlation between the USD/TRY exchange rate and the Food Price Index.
- **Null Hypothesis ($H_0$):** There is no correlation ($r=0$).
- **Test Used:** Pearson Correlation Coefficient.
- **Result:**
  - **P-value:** $< 0.05$
  - **Conclusion:** The null hypothesis is **rejected**. The analysis confirms a statistically significant and strong positive correlation between dollar rates and food inflation.

---

## 📅 Timeline & Progress

| Date       | Task                                              | Status           |
| ---------- | ------------------------------------------------- | ---------------- |
| **28 Nov** | Collect data, conduct EDA, and Hypothesis Testing | ✅ **Completed** |
| **02 Jan** | Apply Machine Learning (Regression Models)        | ✅ **Completed** |
| **09 Jan** | Final Project Submission                          | ⏳ Pending       |

---

## 🛠️ Requirements

To reproduce the analysis, install the required dependencies:

    pip install -r requirements.txt

**Libraries:**

- `pandas`: Data manipulation and analysis
- `numpy`: Numerical operations
- `matplotlib`: Data visualization
- `seaborn`: Advanced statistical data visualization
- `scipy`: Scientific computing and hypothesis testing
- `scikit-learn`: (Planned for future regression models)
