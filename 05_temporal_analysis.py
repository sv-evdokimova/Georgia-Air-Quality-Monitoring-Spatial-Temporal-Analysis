
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(
    DATA_DIR / "air_quality_long.csv",
    parse_dates=["date"]
)

POLLUTANTS = ["PM2.5", "PM10", "NO2"]

# 1. Исключаем пропущенные измерения.
# Подозрительные нули пока оставляем,
# поскольку проверка их достоверности не завершена.
df = df[
    df["pollutant"].isin(POLLUTANTS)
    & df["value"].notna()
].copy()

# 2. Средние значения по станциям за день
daily = (
    df.groupby(
        ["date", "city", "pollutant"],
        as_index=False
    )["value"]
    .mean()
)

# 3. Средние значения по месяцам
daily["month"] = daily["date"].dt.to_period("M")

monthly = (
    daily.groupby(
        ["month", "city", "pollutant"],
        as_index=False
    )["value"]
    .mean()
)

monthly["month"] = monthly["month"].dt.to_timestamp()

# 4. Сохраняем таблицы
daily.to_csv(
    DATA_DIR / "daily_city_averages.csv",
    index=False,
    encoding="utf-8-sig"
)

monthly.to_csv(
    DATA_DIR / "monthly_city_averages.csv",
    index=False,
    encoding="utf-8-sig"
)

# 5. Графики по загрязнителям
for pollutant in POLLUTANTS:

    subset = monthly[
        monthly["pollutant"] == pollutant
    ]

    plt.figure(figsize=(12, 5))

    for city, group in subset.groupby("city"):
        plt.plot(
            group["month"],
            group["value"],
            marker="o",
            markersize=3,
            label=city
        )

    plt.title(
        f"{pollutant}: Monthly Air Pollution, 2024–2025"
    )
    plt.xlabel("Month")
    plt.ylabel("Monthly mean concentration")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    filename = pollutant.replace(".", "_")

    plt.savefig(
        OUTPUT_DIR / f"{filename}_monthly.png",
        dpi=200
    )

    plt.show()

# 6. Таблица сравнения городов
comparison = (
    daily.groupby(["city", "pollutant"])["value"]
    .agg(["mean", "median", "max", "count"])
    .round(2)
)

print("\n=== СРАВНЕНИЕ ГОРОДОВ ===")
print(comparison.to_string())
# Проверка пика PM2.5 в ноябре 2025
november = df[
    (df["pollutant"] == "PM2.5")
    & (df["date"].dt.year == 2025)
    & (df["date"].dt.month == 11)
]

station_stats = (
    november.groupby(["city", "station"])["value"]
    .agg(["count", "mean", "median", "max"])
    .round(2)
)

print("\n=== PM2.5: НОЯБРЬ 2025 ПО СТАНЦИЯМ ===")
print(station_stats.to_string())
# Проверяем NO2 в августе 2025 по станциям Тбилиси
august_no2 = df[
    (df["city"] == "Tbilisi")
    & (df["pollutant"] == "NO2")
    & (df["date"].dt.year == 2025)
    & (df["date"].dt.month == 8)
]

print("\n=== NO2: ТБИЛИСИ, АВГУСТ 2025 ===")

print(
    august_no2.groupby("station")["value"]
    .agg(["count", "mean", "median", "max"])
    .round(2)
    .to_string()
)

print("\n10 самых высоких значений NO2:")

print(
    august_no2.nlargest(10, "value")[
        ["date", "station", "value"]
    ].to_string(index=False)
)
# Сравнение NO2 по станциям Тбилиси за август 2025

august = df[
    (df["city"] == "Tbilisi")
    & (df["pollutant"] == "NO2")
    & (df["date"].dt.year == 2025)
    & (df["date"].dt.month == 8)
]

print("\nNO2 — август 2025, по станциям:")
print(
    august.groupby("station")["value"]
    .agg(["count", "mean", "median", "max"])
    .round(2)
    .to_string()
)

# Сначала считаем среднее по станциям на каждый день,
# затем усредняем полученные значения за месяц.
def monthly_city_mean(data):
    daily_mean = data.groupby("date")["value"].mean()
    return daily_mean.mean()

with_tsrt = monthly_city_mean(august)
without_tsrt = monthly_city_mean(
    august[august["station"] != "TSRT"]
)

print(f"\nС TSRT: {with_tsrt:.2f}")
print(f"Без TSRT: {without_tsrt:.2f}")
print(f"Разница: {with_tsrt - without_tsrt:.2f}")
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(
    "data/processed/air_quality_wide.csv",
    parse_dates=["date"]
)

tsrt = df[df["station"] == "TSRT"].sort_values("date")

plt.figure(figsize=(14, 5))
plt.plot(tsrt["date"], tsrt["NO2"], linewidth=1)

plt.title("TSRT — Daily NO2, 2024–2025")
plt.xlabel("Date")
plt.ylabel("NO2 concentration")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
