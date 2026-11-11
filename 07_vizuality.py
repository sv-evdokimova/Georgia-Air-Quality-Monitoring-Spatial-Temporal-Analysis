import json
from pathlib import Path
import pandas as pd
import folium
import geopandas as gp
import osmnx as ox

DATA_DIR = Path("data/processed")
DATA_DIR.mkdir(parents=True, exist_ok=True)

with open("response.json", encoding="utf-8") as f:
    data = json.load(f)


stations_df = pd.DataFrame([
    {
        "station_id": s["id"],
        "code": s["code"],
        "address_en": s.get("address_en", ""),
        "lat": s["lat"],
        "lon": s["long"],          #: в API это поле называется long, а не lon
        "elev": s.get("elev"),
        "n_equipment": s.get("equipment_count"),
    }
    for s in data
])
print(stations_df)
stations_df.to_csv(DATA_DIR / "stations_coords.csv", index=False)


rows = []
for s in data:
    for eq in s.get("stationequipment_set", []):
        substance = eq["substance"]["name"] if eq.get("substance") else None
        for m in eq.get("data1hour_set", []):
            rows.append({
                "station": s["code"],
                "lat": s["lat"],
                "lon": s["long"],
                "pollutant": substance,
                "date": m["date_time"],
                "value": m["value"],
            })

df = pd.DataFrame(rows)
df["date"] = pd.to_datetime(df["date"])
print(df.head())
print("Всего измерений:", len(df))
df.to_csv(DATA_DIR / "air_quality_long_koor.csv", index=False)

ox.settings.log_console = True
ox.settings.use_cache = True


# Import seasons air quality
measurements = pd.read_csv(
    DATA_DIR / "air_quality_long_seasonal.csv",
    parse_dates=["date"]
)

# Import station
stations = pd.read_csv(
    DATA_DIR / "stations_coords.csv"
)

# Cheacking
print("Столбцы измерений:", measurements.columns.tolist())
print("Столбцы станций:", stations.columns.tolist())

# Add coordinate
add_coo = measurements.merge(
    stations[["code", "lat", "lon"]],
    left_on="station",
    right_on="code",
    how="left",
    validate="many_to_one"
)

# We remove the duplicate column
add_coo = add_coo.drop(columns=["code"])

# Chesking
print("\nПервые строки:")
print(add_coo.head().to_string(index=False))

print("\nСтанции без координат:")
print(
    add_coo.loc[
        add_coo["lat"].isna() | add_coo["lon"].isna(),
        "station"
    ].drop_duplicates().tolist()
)

# Saving
add_coo.to_csv(
    DATA_DIR / "air_quality_long_geo.csv",
    index=False,
    encoding="utf-8-sig"
)
