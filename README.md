# Turkish Food Price Inflation Analysis (2019-2025)

## DSA 210 - Fall 2025 Project Proposal

### Motivation

Turkey has experienced significant economic volatility in recent years, with food prices being particularly sensitive to currency fluctuations and inflation. This project aims to analyze food price trends over 2019-2025 to understand inflation patterns and their impact on consumer purchasing power.

### Data Sources

**Primary Data:**
- **TÜİK (Turkish Statistical Institute):** Official CPI and food price indices
- **Numbeo:** Crowdsourced food and restaurant price data

**Enrichment Data:**
- USD/TRY and EUR/TRY exchange rates
- Economic indicators (GDP, unemployment, interest rates)
- Agricultural production statistics (if available)

### Data Collection Plan

1. Download TÜİK data via web scraping or official sources
2. Extract Numbeo historical data for Turkish cities
3. Collect exchange rate data from TCMB
4. Integrate and validate data from multiple sources
5. Handle missing values and create derived features

### Planned Analysis

**Exploratory Analysis:**
- Time series visualization of food inflation trends
- Comparison across food categories (bread, dairy, meat, produce)
- Correlation analysis with exchange rates and economic indicators
- Seasonal pattern detection

**Hypothesis Testing:**
- Currency depreciation vs food price correlation
- COVID-19 period impact on food prices
- Category-wise inflation differences

**Machine Learning:**
- Time series forecasting models (ARIMA, Prophet, or similar)
- Price prediction based on economic indicators
- Model evaluation and comparison

### Tools & Technologies
```
Python libraries:
- pandas, numpy (data manipulation)
- matplotlib, seaborn, plotly (visualization)
- scipy, statsmodels (statistical analysis)
- scikit-learn (machine learning)
```

### Expected Outcomes

- Interactive visualizations showing inflation trends
- Statistical analysis of price patterns
- Predictive models for future price trends
- Insights on economic factors affecting food prices

### Timeline

- **Nov 28:** Data collection and exploratory analysis complete
- **Jan 2:** Machine learning models implemented
- **Jan 9:** Final submission with full documentation

### Limitations

- Data availability and quality from public sources
- Difficulty capturing all economic variables
- Numbeo data is crowdsourced and may have biases
