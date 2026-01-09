from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "food_inflation_data.csv"
IMG_DIR = BASE_DIR / "images"

PRICE_COLS = ["Bread_Price", "Milk_Price", "Meat_Price"]
INDEX_COLS = ["Bread_Index", "Milk_Index", "Meat_Index"]


def add_food_price_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if all(col in df.columns for col in INDEX_COLS):
        df["Food_Price_Index"] = df[INDEX_COLS].mean(axis=1)
        return df
    if all(col in df.columns for col in PRICE_COLS):
        base_row = df.iloc[0]
        for col in PRICE_COLS:
            df[f"{col}_Index"] = df[col] / base_row[col] * 100
        index_cols = [f"{col}_Index" for col in PRICE_COLS]
        df["Food_Price_Index"] = df[index_cols].mean(axis=1)
        return df
    raise ValueError("Expected price or index columns for food items.")


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    df = add_food_price_index(df)

    IMG_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(14, 6))
    ax1 = sns.lineplot(x="Date", y="Food_Price_Index", data=df, color="orange", label="Food Price Index")
    ax1.set_ylabel("Food Price Index (base=100)", color="orange")
    ax2 = plt.twinx()
    sns.lineplot(
        x="Date",
        y="USD_TRY",
        data=df,
        ax=ax2,
        color="green",
        linestyle="--",
        label="USD/TRY",
    )
    ax2.set_ylabel("USD/TRY", color="green")
    plt.title("Food Prices vs USD/TRY (2019-2024)")
    plt.tight_layout()
    plt.savefig(IMG_DIR / "Figure_1.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 6))
    sns.scatterplot(x="USD_TRY", y="Food_Price_Index", data=df, alpha=0.7)
    plt.title("USD/TRY vs Food Price Index")
    plt.xlabel("USD/TRY")
    plt.ylabel("Food Price Index")
    plt.tight_layout()
    plt.savefig(IMG_DIR / "Figure_2.png", dpi=200)
    plt.close()

    r_value, p_value = stats.pearsonr(df["USD_TRY"], df["Food_Price_Index"])
    print("Correlation (USD_TRY vs Food_Price_Index)")
    print(f"r = {r_value:.4f}")
    print(f"p = {p_value:.4e}")


if __name__ == "__main__":
    main()
