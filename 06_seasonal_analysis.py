
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

# 1. Определяем сезоны
month_to_season = {
    1: "winter", 2: "winter",
    3: "spring", 4: "spring", 5: "spring",
    6: "summer", 7: "summer", 8: "summer",
    9: "autumn", 10: "autumn", 11: "autumn",
    12: "winter"
}

season_order = ["winter", "spring", "summer", "autumn"]
POLLUTANTS = ["PM2.5", "PM10", "NO2"]

df["season"] = df["date"].dt.month.map(month_to_season)

# 2. Твоя функция сезонных средних
def add_seasonal_averages(
    df: pd.DataFrame,
    station_col: str = "station",
    pollutant_col: str = "pollutant",
    value_col: str = "value",
    season_col: str = "season"
) -> pd.DataFrame:

    result = df.copy()

    result["average_value_season"] = (
        result.groupby(
            [station_col, pollutant_col, season_col],
            dropna=False
        )[value_col].transform("mean")
    )

    return result


df = add_seasonal_averages(df)

df.to_csv(
    DATA_DIR / "air_quality_long_seasonal.csv",
    index=False,
    encoding="utf-8-sig"
)

# 3. Оставляем нужные загрязнители
analysis = df[
    df["pollutant"].isin(POLLUTANTS)
    & df["value"].notna()
].copy()

# 4. Средние по каждой станции и сезону
# (2024 и 2025 объединены)
station_season = (
    analysis.groupby(
        ["city", "station", "pollutant", "season"],
        as_index=False
    )["value"]
    .mean()
)

# 5. Среднее по городу:
# каждой станции даём одинаковый вес
city_season = (
    station_season.groupby(
        ["city", "pollutant", "season"],
        as_index=False
    )["value"]
    .mean()
)

# 6. Строим по одному графику на загрязнитель
for pollutant in POLLUTANTS:

    subset = city_season[
        city_season["pollutant"] == pollutant
    ]

    plot_data = subset.pivot(
        index="season",
        columns="city",
        values="value"
    ).reindex(season_order)

    ax = plot_data.plot(
        kind="bar",
        figsize=(9, 5),
        width=0.75
    )

    ax.set_title(
        f"Seasonal Mean {pollutant}: Tbilisi vs Rustavi"
    )
    ax.set_xlabel("Season")
    ax.set_ylabel("Mean concentration")
    ax.tick_params(axis="x", rotation=0)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(title="City")

    plt.tight_layout()

    filename = pollutant.replace(".", "_")

    plt.savefig(
        OUTPUT_DIR / f"{filename}_seasonal.png",
        dpi=200
    )

    plt.show()

# 7. Итоговая таблица
print("\n=== СЕЗОННЫЕ СРЕДНИЕ ПО ГОРОДАМ ===")

print(
    city_season.pivot_table(
        index=["pollutant", "season"],
        columns="city",
        values="value"
    ).round(2).to_string()
)
