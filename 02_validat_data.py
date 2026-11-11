import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")

files = sorted(DATA_DIR.glob("*.xlsx"))

print("Всего файлов:", len(files))

# Посмотрим один файл
file = DATA_DIR / "ORN01_2024-01.xlsx"

xls = pd.ExcelFile(file)

print("Листы:", xls.sheet_names)

for sheet in xls.sheet_names:
    df = pd.read_excel(file, sheet_name=sheet, header=None)

    print(f"\nЛист: {sheet}")
    print("Размер:", df.shape)
    print(df.head(10).to_string(index=False, header=False))
