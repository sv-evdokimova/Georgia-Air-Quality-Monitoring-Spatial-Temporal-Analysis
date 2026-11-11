
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/processed")
df = pd.read_csv(
    DATA_DIR / "air_quality_wide.csv",
    parse_dates=["date"]
)

pollutants = ["NO2", "SO2", "PM2.5", "PM10", "O3", "CO"]
calendar = pd.date_range("2024-01-01", "2025-12-31")

# 1. Отсутствующие календарные дни
print("=== ОТСУТСТВУЮЩИЕ ДАТЫ ===")

for station in sorted(df["station"].unique()):
    observed = pd.DatetimeIndex(
        df.loc[df["station"] == station, "date"]
    )
    missing_dates = calendar.difference(observed)

    print(
        f"{station}: {len(missing_dates)} дней отсутствует"
    )

    if len(missing_dates):
        print(
            "  Даты:",
            missing_dates.strftime("%Y-%m-%d").tolist()
        )

# 2. Полнота измерений
print("\n=== ПОЛНОТА ДАННЫХ, % ===")

completeness = (
    df.groupby(["city", "station"])[pollutants]
    .apply(lambda x: x.notna().mean() * 100)
    .round(1)
)

print(completeness.to_string())

# 3. Подозрительные нули
print("\n=== ОДНОВРЕМЕННЫЕ НУЛИ ГАЗОВ ===")

gases = ["NO2", "SO2", "O3", "CO"]

# Считаем только строки, где все четыре
# показателя присутствуют и равны нулю
all_zero = df[gases].notna().all(axis=1) & (
    df[gases].eq(0).all(axis=1)
)

print("Подозрительных дней:", all_zero.sum())

print(
    df.loc[all_zero, ["date", "station"] + gases]
    .head(30)
    .to_string(index=False)
)

# 4. Отрицательные значения
print("\n=== ОТРИЦАТЕЛЬНЫЕ ЗНАЧЕНИЯ ===")

print((df[pollutants] < 0).sum().to_string())

# 5. Диапазоны измерений
print("\n=== СТАТИСТИКА ===")

print(
    df[pollutants]
    .describe()
    .round(2)
    .to_string()
)

# 6. Сохраняем результаты
completeness.to_csv(
    DATA_DIR / "completeness_by_station.csv",
    encoding="utf-8-sig"
)

df.loc[all_zero].to_csv(
    DATA_DIR / "suspicious_zero_days.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nПроверка завершена.")
