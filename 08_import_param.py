import requests
import pandas as pd
from pathlib import Path



url = "https://www.air.gov.ge/api/get_data_1hour/"
params = {
    "from_date_time": "2026-11-08T12:00:00",
    "to_date_time": "2026-11-10T11:00:00",
    "substance": "all",
    "municipality_id": "all",
    "last_data": "false",
    "chart": "false",
    "format": "json",
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://www.air.gov.ge/en/",
}

response = requests.get(url, params=params, headers=headers, timeout=30)
response.raise_for_status()
data = response.json()


with open("response.json", "w", encoding="utf-8") as f:
    import json
    json.dump(data, f, ensure_ascii=False)
