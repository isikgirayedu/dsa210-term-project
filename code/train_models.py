# code/train_models.py
import os
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parents[1]
PRICE_COLS = ["Bread_Price", "Milk_Price", "Meat_Price"]
INDEX_COLS = ["Bread_Index", "Milk_Index", "Meat_Index"]


@dataclass
class Config:
    data_path: str = str(BASE_DIR / "data" / "food_inflation_data.csv")
    target_col: str = "Food_Price_Index"
    date_col: str = "Date"
    output_predictions_path: str = str(BASE_DIR / "data" / "predictions.csv")
    output_metrics_path: str = str(BASE_DIR / "data" / "metrics.csv")
    output_plot_path: str = str(BASE_DIR / "images" / "prediction_plot.png")
    n_splits: int = 5
    forecast_horizon: int = 1  # 1-month ahead


def make_features(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    df = df.copy()
    df[cfg.date_col] = pd.to_datetime(df[cfg.date_col])
    df = df.sort_values(cfg.date_col).reset_index(drop=True)
    if cfg.target_col not in df.columns:
        if all(col in df.columns for col in INDEX_COLS):
            df[cfg.target_col] = df[INDEX_COLS].mean(axis=1)
        elif all(col in df.columns for col in PRICE_COLS):
            base_row = df.iloc[0]
            for col in PRICE_COLS:
                df[f"{col}_Index"] = df[col] / base_row[col] * 100
            index_cols = [f"{col}_Index" for col in PRICE_COLS]
            df[cfg.target_col] = df[index_cols].mean(axis=1)
        else:
            raise ValueError("Food_Price_Index missing and required price/index columns not found.")

    # Basic time features
    df["month"] = df[cfg.date_col].dt.month
    df["year"] = df[cfg.date_col].dt.year

    # Lag features for predictors and target (common in time series regression)
    # If you also have "USD_TRY", it will be used automatically.
    cols_to_lag = [c for c in df.columns if c not in [cfg.date_col]]
    for col in cols_to_lag:
        for lag in [1, 2, 3, 6, 12]:
            df[f"{col}_lag{lag}"] = df[col].shift(lag)

    # Rolling stats for target (optional but useful)
    df[f"{cfg.target_col}_roll3_mean"] = df[cfg.target_col].rolling(3).mean().shift(1)
    df[f"{cfg.target_col}_roll6_mean"] = df[cfg.target_col].rolling(6).mean().shift(1)

    # 1-step-ahead target
    df["y"] = df[cfg.target_col].shift(-cfg.forecast_horizon)

    # Drop rows with NA from lags/rolls/shift
    df = df.dropna().reset_index(drop=True)
    return df


def get_models(random_state: int = 42):
    return {
        "LinearRegression": Pipeline([("scaler", StandardScaler()), ("model", LinearRegression())]),
        "Ridge": Pipeline([("scaler", StandardScaler()), ("model", Ridge(alpha=1.0))]),
        "Lasso": Pipeline([("scaler", StandardScaler()), ("model", Lasso(alpha=0.001))]),
        "RandomForest": RandomForestRegressor(
            n_estimators=400, max_depth=6, random_state=random_state
        ),
    }


def evaluate_models(X: np.ndarray, y: np.ndarray, dates: np.ndarray, models: dict, cfg: Config):
    tscv = TimeSeriesSplit(n_splits=cfg.n_splits)
    metrics_rows = []
    oof_preds = {name: np.full_like(y, fill_value=np.nan, dtype=float) for name in models.keys()}

    for name, model in models.items():
        for fold, (train_idx, test_idx) in enumerate(tscv.split(X), start=1):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            model.fit(X_train, y_train)
            pred = model.predict(X_test)

            oof_preds[name][test_idx] = pred

            mse = mean_squared_error(y_test, pred)
            metrics_rows.append({
                "model": name,
                "fold": fold,
                "MAE": mean_absolute_error(y_test, pred),
                "RMSE": np.sqrt(mse),
                "R2": r2_score(y_test, pred),
            })

    metrics_df = pd.DataFrame(metrics_rows)
    # Aggregate per model
    summary = metrics_df.groupby("model")[["MAE", "RMSE", "R2"]].mean().sort_values("RMSE")
    return metrics_df, summary, oof_preds


def save_plot(dates, y_true, y_pred, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.figure()
    plt.plot(dates, y_true, label="Actual")
    plt.plot(dates, y_pred, label="Predicted")
    plt.title("Food Price Index: Actual vs Predicted (OOF)")
    plt.xlabel("Date")
    plt.ylabel("Index")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def main():
    cfg = Config()

    df_raw = pd.read_csv(cfg.data_path)
    df = make_features(df_raw, cfg)

    # Feature set: use all engineered columns except date + raw target columns + y
    drop_cols = {cfg.date_col, cfg.target_col, "y"}
    feature_cols = [c for c in df.columns if c not in drop_cols and not c.endswith("_lag0")]

    X = df[feature_cols].values
    y = df["y"].values
    dates = df[cfg.date_col].values

    models = get_models()
    metrics_df, summary, oof_preds = evaluate_models(X, y, dates, models, cfg)

    # Pick best model by average RMSE
    best_model = summary.index[0]
    best_pred = oof_preds[best_model]

    # Save outputs
    os.makedirs("data", exist_ok=True)
    metrics_df.to_csv(cfg.output_metrics_path, index=False)

    preds_df = pd.DataFrame({
        "Date": pd.to_datetime(dates),
        "y_true": y,
        f"y_pred_{best_model}": best_pred,
    })
    preds_df.to_csv(cfg.output_predictions_path, index=False)

    save_plot(pd.to_datetime(dates), y, best_pred, cfg.output_plot_path)

    print("\n=== CV Summary (mean over folds) ===")
    print(summary)
    print(f"\nBest model: {best_model}")
    print(f"Saved metrics -> {cfg.output_metrics_path}")
    print(f"Saved predictions -> {cfg.output_predictions_path}")
    print(f"Saved plot -> {cfg.output_plot_path}")


if __name__ == "__main__":
    main()
