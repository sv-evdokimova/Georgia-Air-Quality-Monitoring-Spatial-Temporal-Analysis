import requests
import pandas as pd
import time
from pathlib import Path

BASE_URL = "https://www.air.gov.ge/en/reports_page"

STATIONS = {
    "AGMS": "Tbilisi",
    "ORN01": "Tbilisi",
    "TSRT": "Tbilisi",
    "KZBG": "Tbilisi",
    "RST18": "Rustavi",
    "ORN02": "Rustavi",
}

START_YEAR = 2024
END_YEAR = 2025

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()

downloaded = []
failed = []

for station, city in STATIONS.items():

    for year in range(START_YEAR, END_YEAR + 1):

        for month in range(1, 13):

            date_from = f"{year}-{month:02d}"

            params = {
                "station": station,
                "report_type": "monthly",
                "date_from": date_from,
                "export_type": "xlsx",
            }

            filename = OUTPUT_DIR / f"{station}_{date_from}.xlsx"

            if filename.exists():
                print("Уже существует:", filename.name)
                continue

            try:
                response = session.get(
                    BASE_URL,
                    params=params,
                    timeout=60
                )
                response.raise_for_status()

                if not response.content.startswith(b"PK\x03\x04"):
                    raise ValueError("Сервер вернул не XLSX")

                filename.write_bytes(response.content)

                downloaded.append({
                    "station": station,
                    "city": city,
                    "month": date_from,
                    "file": str(filename),
                })

                print("OK:", filename.name)

            except (requests.RequestException, ValueError) as e:
                failed.append({
                    "station": station,
                    "month": date_from,
                    "error": str(e),
                })

                print("ERROR:", station, date_from, e)

            time.sleep(1)

print("\nСкачано:", len(downloaded))
print("Ошибок:", len(failed))
