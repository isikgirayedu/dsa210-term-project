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
    index_cols = [col for col in INDEX_COLS if col in df.columns]
    df["Food_Price_Index_MoM"] = df["Food_Price_Index"].pct_change() * 100
    df["USD_TRY_MoM"] = df["USD_TRY"].pct_change() * 100

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

    if index_cols:
        label_map = {
            "Bread_Index": "Bread Index",
            "Milk_Index": "Milk Index",
            "Meat_Index": "Meat Index",
        }
        color_map = {
            "Bread_Index": "#1f77b4",
            "Milk_Index": "#ff7f0e",
            "Meat_Index": "#2ca02c",
        }
        plt.figure(figsize=(12, 6))
        for col in index_cols:
            sns.lineplot(
                x="Date",
                y=col,
                data=df,
                label=label_map.get(col, col),
                color=color_map.get(col),
            )
        sns.lineplot(
            x="Date",
            y="Food_Price_Index",
            data=df,
            label="Food Price Index",
            color="black",
            linestyle="--",
        )
        plt.title("Item Indices vs Composite Food Price Index")
        plt.xlabel("Date")
        plt.ylabel("Index (2015=100)")
        plt.tight_layout()
        plt.savefig(IMG_DIR / "Figure_3.png", dpi=200)
        plt.close()

    plt.figure(figsize=(12, 6))
    sns.lineplot(
        x="Date",
        y="Food_Price_Index_MoM",
        data=df,
        label="Food Price Index MoM (%)",
        color="orange",
    )
    sns.lineplot(
        x="Date",
        y="USD_TRY_MoM",
        data=df,
        label="USD/TRY MoM (%)",
        color="green",
    )
    plt.axhline(0, color="gray", linestyle="--", linewidth=1)
    plt.title("Month-over-Month Change (%)")
    plt.xlabel("Date")
    plt.ylabel("Percent Change")
    plt.tight_layout()
    plt.savefig(IMG_DIR / "Figure_4.png", dpi=200)
    plt.close()

    r_value, p_value = stats.pearsonr(df["USD_TRY"], df["Food_Price_Index"])
    print("Correlation (USD_TRY vs Food_Price_Index)")
    print(f"r = {r_value:.4f}")
    print(f"p = {p_value:.4e}")


if __name__ == "__main__":
    main()
