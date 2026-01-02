import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor

RANDOM_STATE = 42

def metrics(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = mean_squared_error(y_true, y_pred, squared=False)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    r2 = r2_score(y_true, y_pred)
    return {"MAE": mae, "RMSE": rmse, "MAPE_%": mape, "R2": r2}

def main(data_path="../data/turkey_food_inflation_dataset.csv"):
    df = pd.read_csv(data_path)
    date_col_candidates = [c for c in df.columns if c.lower() in {"date","month","timestamp","time"}]
    if not date_col_candidates:
        raise ValueError("No date column found.")
    date_col = date_col_candidates[0]
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col).reset_index(drop=True)

    target_candidates = [c for c in df.columns if c.lower() in {"food_price_index","foodpriceindex","food_index","food_index_value"}]
    if not target_candidates:
        raise ValueError("Target column not found.")
    target_col = target_candidates[0]

    df["year"] = df[date_col].dt.year
    df["month"] = df[date_col].dt.month
    df["t"] = np.arange(len(df))
    df[f"{target_col}_lag_1"] = df[target_col].shift(1)
    df[f"{target_col}_lag_12"] = df[target_col].shift(12)
    df[f"{target_col}_roll_3"] = df[target_col].shift(1).rolling(3).mean()
    df[f"{target_col}_roll_6"] = df[target_col].shift(1).rolling(6).mean()

    df_model = df.dropna(subset=[f"{target_col}_lag_1"]).reset_index(drop=True)

    numeric_cols = df_model.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != target_col]
    cat_cols = [c for c in df_model.columns if df_model[c].dtype == "object" and c not in {date_col, target_col}]

    X = df_model[numeric_cols + cat_cols]
    y = df_model[target_col]

    split_idx = int(len(df_model) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    # Baseline
    baseline = metrics(y_test, X_test[f"{target_col}_lag_1"].values)

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    preprocess = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, cat_cols),
        ]
    )

    models = {
        "LinearRegression": LinearRegression(),
        "Ridge(alpha=1.0)": Ridge(alpha=1.0, random_state=RANDOM_STATE),
        "Lasso(alpha=0.001)": Lasso(alpha=0.001, random_state=RANDOM_STATE, max_iter=10000),
        "RandomForest": RandomForestRegressor(n_estimators=500, random_state=RANDOM_STATE, n_jobs=-1),
        "HistGradientBoosting": HistGradientBoostingRegressor(random_state=RANDOM_STATE),
    }

    out = []
    for name, model in models.items():
        pipe = Pipeline(steps=[("preprocess", preprocess), ("model", model)])
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        res = metrics(y_test, pred)
        res["Model"] = name
        out.append(res)

    res_df = pd.DataFrame(out).set_index("Model").sort_values("RMSE")
    return baseline, res_df

if __name__ == "__main__":
    baseline, res_df = main()
    print("Baseline (Naive lag_1):", baseline)
    print(res_df)
