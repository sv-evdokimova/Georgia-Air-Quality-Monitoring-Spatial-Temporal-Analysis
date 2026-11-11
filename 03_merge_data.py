
from pathlib import Path
import pandas as pd

# 1. Настройки
DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STATIONS = {
    "AGMS": "Tbilisi",
    "ORN01": "Tbilisi",
    "TSRT": "Tbilisi",
    "KZBG": "Tbilisi",
    "RST18": "Rustavi",
    "ORN02": "Rustavi",
}

POLLUTANTS = ["NO2", "SO2", "PM2.5", "PM10", "O3", "CO"]

all_data = []
file_log = []

# 2. Обрабатываем каждый Excel
for file in sorted(DATA_DIR.glob("*.xlsx")):
    try:
        station, month = file.stem.split("_", 1)

        if station not in STATIONS:
            raise ValueError(f"Неизвестная станция: {station}")

        raw = pd.read_excel(
            file,
            header=None,
            engine="openpyxl"
        )

        if raw.shape[1] != 7:
            raise ValueError(
                f"Ожидалось 7 столбцов, найдено {raw.shape[1]}"
            )

        # Первая строка содержит месяц
        report_month = str(raw.iloc[0, 0]).strip()[:7]

        if report_month != month:
            raise ValueError(
                f"Месяц в файле {report_month} "
                f"не совпадает с именем {month}"
            )

        df = raw.iloc[1:].copy()
        df.columns = ["day"] + POLLUTANTS

        df["day"] = pd.to_numeric(
            df["day"], errors="coerce"
        )

        df = df.dropna(subset=["day"])
        df["day"] = df["day"].astype(int)

        df["date"] = pd.to_datetime(
            month + "-" + df["day"].astype(str).str.zfill(2),
            errors="coerce"
        )

        if df["date"].isna().any():
            raise ValueError("Обнаружены некорректные даты")

        for pollutant in POLLUTANTS:
            df[pollutant] = pd.to_numeric(
                df[pollutant].replace("*", pd.NA),
                errors="coerce"
            )

        df["station"] = station
        df["city"] = STATIONS[station]

        all_data.append(df)

        file_log.append({
            "file": file.name,
            "status": "OK",
            "days": len(df),
            "error": ""
        })

    except Exception as e:
        file_log.append({
            "file": file.name,
            "status": "ERROR",
            "days": 0,
            "error": str(e)
        })

# 3. Проверяем результат
log = pd.DataFrame(file_log)
log.to_csv(
    OUTPUT_DIR / "import_log.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Файлов обработано:", len(log))
print("Успешно:", (log["status"] == "OK").sum())
print("Ошибок:", (log["status"] == "ERROR").sum())

if not all_data:
    raise RuntimeError("Не удалось прочитать ни одного файла")

# 4. Объединяем в широкую таблицу
wide = pd.concat(all_data, ignore_index=True)

wide = wide[
    ["date", "city", "station"] + POLLUTANTS
].sort_values(["city", "station", "date"])

# Проверяем дубликаты дат внутри станции
duplicates = wide.duplicated(["station", "date"]).sum()
print("Дубликатов станция-дата:", duplicates)

# 5. Преобразуем в длинный формат
long = wide.melt(
    id_vars=["date", "city", "station"],
    value_vars=POLLUTANTS,
    var_name="pollutant",
    value_name="value"
)

# Флаг для проверки нулевых измерений
long["zero_flag"] = long["value"].eq(0)

# 6. Сохраняем результаты
wide.to_csv(
    OUTPUT_DIR / "air_quality_wide.csv",
    index=False,
    encoding="utf-8-sig"
)

long.to_csv(
    OUTPUT_DIR / "air_quality_long.csv",
    index=False,
    encoding="utf-8-sig"
)

# 7. Первичная статистика
print("\nВсего строк (дни × станции):", len(wide))
print("Всего измерений, включая пропуски:", len(long))
print("Измерений без пропусков:", long["value"].notna().sum())
print("Нулевых значений:", long["zero_flag"].sum())

print("\nПериод:")
print(wide["date"].min(), "—", wide["date"].max())

print("\nСтрок по станциям:")
print(wide.groupby(["city", "station"]).size())

print("\nПропуски по загрязнителям:")
print(long.groupby("pollutant")["value"].apply(
    lambda x: x.isna().sum()
))

print("\nПервые 10 строк:")
print(long.head(10).to_string(index=False))

if (log["status"] == "ERROR").any():
    print("\nОшибки импорта:")
    print(
        log.loc[log["status"] == "ERROR"]
        .to_string(index=False)
    )
