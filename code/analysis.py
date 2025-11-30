import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

np.random.seed(42) 

dates = pd.date_range(start='2019-01-01', end='2025-01-01', freq='M')
n = len(dates)

usd_trend = np.linspace(5.5, 34.0, n)
usd_fluctuation = np.random.normal(0, 0.8, n) 
usd_rates = usd_trend + usd_fluctuation
usd_rates = np.maximum(usd_rates, 5.0) 

base_inflation = np.linspace(100, 1800, n) 
food_noise = np.random.normal(0, 20, n)
food_index = base_inflation + (usd_rates * 10) + food_noise

df = pd.DataFrame({
    'Date': dates,
    'USD_TRY': np.round(usd_rates, 2),
    'Food_Price_Index': np.round(food_index, 2)
})

df.to_csv('turkey_food_inflation_dataset.csv', index=False)
print("✅ Veri seti oluşturuldu: 'turkey_food_inflation_dataset.csv'")


print("\n--- Veri Seti Bilgisi ---")
print(df.info())
print("\n--- İstatistiksel Özet ---")
print(df.describe())

plt.figure(figsize=(14, 6))

ax1 = sns.lineplot(x='Date', y='Food_Price_Index', data=df, color='orange', label='Gıda Fiyat Endeksi')
ax1.set_ylabel('Gıda Fiyat Endeksi (Baz=100)', color='orange')
plt.legend(loc='upper left')

ax2 = plt.twinx()
sns.lineplot(x='Date', y='USD_TRY', data=df, ax=ax2, color='green', linestyle='--', label='USD/TRY Kuru')
ax2.set_ylabel('Dolar Kuru (TL)', color='green')
plt.legend(loc='upper right')

plt.title('Türkiye Gıda Enflasyonu ve Dolar Kuru İlişkisi (2019-2025)')
plt.show()

plt.figure(figsize=(8, 6))
sns.scatterplot(x='USD_TRY', y='Food_Price_Index', data=df, alpha=0.6)
plt.title('Dolar Kuru vs. Gıda Fiyat Endeksi')
plt.xlabel('Dolar Kuru (TL)')
plt.ylabel('Gıda Fiyat Endeksi')
plt.show()


r_katsayisi, p_value = stats.pearsonr(df['USD_TRY'], df['Food_Price_Index'])

print("\n--- Hipotez Testi Sonucu ---")
print(f"Korelasyon Katsayısı (r): {r_katsayisi:.4f}")
print(f"P-Değeri: {p_value:.4e}")

if p_value < 0.05:
    print("SONUÇ: H0 reddedildi. Dolar kuru ile gıda fiyatları arasında GÜÇLÜ ve ANLAMLI bir ilişki var.")
else:
    print("SONUÇ: Anlamlı bir ilişki bulunamadı.")