# Georgia Air Quality Monitoring: Spatial & Temporal Analysis

![Python](https://img.shields.io/badge/Python-3.14-blue) ![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458) ![Folium](https://img.shields.io/badge/Folium-Interactive%20Maps-77B829) ![GeoPandas](https://img.shields.io/badge/GeoPandas-GIS-139C5A)

## Project overview

This project explores spatial and temporal patterns of ambient air pollution in **Tbilisi and Rustavi, Georgia**, using publicly available measurements from the Georgian air-quality monitoring network. The analysis focuses on **2024–2025**, comparing pollutant concentrations across monitoring stations, cities, and seasons.

The workflow combines automated data collection, quality assessment, time-series analysis, and interactive geographic visualization.

## Research questions

- How do PM2.5, PM10, and NO₂ concentrations vary across seasons?
- How do measurements differ between Tbilisi and Rustavi?
- Which monitoring stations record higher or lower average concentrations?
- How do missing observations and station-level variability affect interpretation?

## Study area and monitoring stations

The historical dataset includes six station codes:

| City | Station codes |
| --- | --- |
| Tbilisi | `AGMS`, `ORN01`, `TSRT`, `KZBG` |
| Rustavi | `RST18`, `ORN02` |

**Mapping limitation:** Coordinates have been obtained for five stations. `AGMS` is retained in the analytical dataset but excluded from point maps until its coordinates are verified.

## Data sources

- **Georgian National Environmental Agency — Air Quality Portal:** [air.gov.ge](https://www.air.gov.ge/en/reports_page)
- Monthly XLSX reports for January 2024–December 2025, downloaded by station.
- Station metadata and coordinates obtained from a station-information JSON response.
- **OpenStreetMap** tiles as the basemap for the interactive visualization.

### Pollutants

The original reports include `NO2`, `SO2`, `PM2.5`, `PM10`, `O3`, and `CO`. Current seasonal maps focus on **PM2.5, PM10, and NO₂**. Concentrations shown on these maps are labeled in **µg/m³**; check the original reporting units before extending maps to other pollutants, particularly CO.

## Methodology

1. **Data acquisition:** Download monthly XLSX reports for each station and month.
2. **Data integration:** Standardize dates, station codes, and pollutant columns; create wide- and long-format datasets.
3. **Quality assessment:** Identify missing observations, duplicates, zero values, and unusual measurements without automatically removing valid-looking extremes.
4. **Temporal analysis:** Compute daily and monthly summaries and visualize trends.
5. **Seasonal analysis:** Assign months to meteorological seasons and calculate station-level seasonal means across the study period.
6. **Spatial preparation:** Join measurements to station coordinates using station codes; retain unmatched stations for non-spatial analysis.
7. **Interactive mapping:** Create 12 pollutant–season combinations in Folium with consistent color ranges across seasons for each pollutant.

**Season definitions:** Winter = December–February; Spring = March–May; Summer = June–August; Autumn = September–November. The current seasonal summaries pool matching months from 2024 and 2025; they are not individual-year seasonal comparisons.

**Interpretation:** The maps show **station measurements**, not continuous pollution surfaces. No spatial interpolation is implied.

## Project structure

The following is a suggested repository layout. Adjust filenames to match the files you publish.

```text
Georgia-Air-Quality-Monitoring/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                       # Downloaded monthly XLSX reports
│   └── processed/
│       ├── air_quality_wide.csv
│       ├── air_quality_long.csv
│       ├── air_quality_long_seasonal.csv
│       ├── air_quality_long_geo.csv
│       └── stations_coords.csv
├── outputs/
│   ├── figures/                   # Time-series and seasonal charts
|   |   ├── PM10_seasonal.png
|   |   ├── PM2_5_seasonal.png
|   |   └── NO2_seasonal.png
|   |    
│   └── maps/
│       └── air_quality_seasonal_map.html
├── images/
|       └── images/imagesair_quality_map.JPG        # Screenshots for this README
├── 03_merge_data.py
├── 04_data_quality.py
├── 05_temporal_analysis.py
├── 09_air_quality_map.py
└── ...                             # Additional data collection / analysis scripts
```

## Getting started

### Requirements

- Python 3.14 (project development environment)
- Python packages used in the workflow: `pandas`, `openpyxl`, `requests`, `matplotlib`, `folium`, `branca`, `geopandas`

Install dependencies:

```bash
python -m pip install pandas openpyxl requests matplotlib folium branca geopandas
```

### Run the analysis

From the repository root, after obtaining the source data:

```bash
python 03_merge_data.py
python 04_data_quality.py
python 05_temporal_analysis.py
python 09_air_quality_map.py
```

> Other preprocessing scripts, including the seasonal-analysis and coordinate-join steps, must be run before the map script if their output CSV files have not already been generated. Update this section with the exact script names and execution order in the final repository.

Open `outputs/maps/air_quality_seasonal_map.html` in a web browser. Internet access is normally required to load OpenStreetMap basemap tiles.

## Interactive map

The Folium map provides pollutant and season selections, station markers, popups with mean concentrations, and a concentration legend. Color scales are held constant **across seasons within each pollutant** to support seasonal comparisons.

![Interactive Air Quality Map](output/figures/ sair_quality_map.JPG)

*Replace the placeholder image with an actual screenshot saved at `images/air_quality_map.png`.*

If you publish the HTML map, add a link here:

**[Open Interactive Air Quality Map]**(https://si187971-dev.github.io/Georgia-Air-Quality-Monitoring-Spatial-Temporal-Analysis/map.html)

## Preliminary data coverage

The processed 2024–2025 dataset contains:

| Metric | Value |
| --- | ---: |
| Monthly XLSX files processed | 144 |
| Monitoring stations | 6 |
| Station-day records | 4,333 |
| Pollutant observations, including missing values | 25,998 |
| Non-missing pollutant observations | 22,717 |
| Duplicate station-date records | 0 |

These are processing checks, **not** claims of complete daily coverage for every station and pollutant.

## Findings

*Complete this section after reviewing the final plots and tables.*

- **Seasonality:**
As shown in the graphs, the concentrations of both particulate matter and NO2 are markedly higher during the autumn and winter periods. For 
NO 2, the values range from 18 to 38 μg/m3 in Rustavi and from 41 to 54 μg/m3 in Tbilisi. For PM 2.5, the ranges are 16–35 μg/m3
(Rustavi) and 11–24 μg/m3 (Tbilisi); for PM 10, they are 38–51 μg/m3 (Rustavi) and 29–40 μg/m3 (Tbilisi).
These elevated and variable concentrations may negatively affect the health and well-being of the residents.

Tbilisi is a considerably larger city, and, as the graphs show, the total volume of exhaust-gas emissions there is greater. Nevertheless, in terms of particulate-matter concentrations, Rustavi shows higher values (for example, PM10
up to 51 μg/m3 versus 40 μg/m3 in Tbilisi, and PM 2.5 up to 35 μg/m3 versus 24 μg/m3). This suggests that factors other than the sheer volume of traffic emissions — such as local topography, heating systems, or meteorological 
conditions — play an important role.

![PM10_seasonal](output/figures/PM10_seasonal.png)
![PM2_5_seasonal.png](output/figures/PM2_5_seasonal.png)
![NO2_seasonal.png](output/figures/NO2_seasonal.png)
- **Tbilisi vs. Rustavi:** [Insert a comparison supported by the data.]
- **Station-level differences:** [Identify noteworthy variation and its limitations.]
- **Data quality:** [Summarize missingness and any measurement anomalies.]

## Limitations

- Station measurements describe conditions at monitoring sites; they do not represent every location in either city.
- Missing values and differences in station coverage may affect comparisons.
- Some observations are unusually high; they are retained unless a documented quality-control reason supports exclusion.
- `AGMS` is not plotted until its coordinates are confirmed.
- Seasonal means currently combine both study years and do not capture within-season variation.
- The OpenStreetMap basemap requires an internet connection in typical HTML use.

## Tools and technologies

**Python · pandas · NumPy · Matplotlib · GeoPandas · Folium · Branca · Requests · OpenPyXL · OpenStreetMap · VS Code**

## Future work

- Verify the coordinates of `AGMS` and include it on the map.
- Add year-specific seasonal comparisons and station-level trend views.
- Improve map controls and legends and publish a hosted interactive map.
- Document pollutant-specific units and quality-assurance metadata.

## Data attribution

Air-quality measurements: **Georgian National Environmental Agency**, [air.gov.ge](https://www.air.gov.ge/en/reports_page). Basemap: **© OpenStreetMap contributors**. Check applicable data-use and redistribution terms before uploading raw source files to a public repository.

## Author

**[(sv-evdokimova)]**  
GIS & Data Science Portfolio Project  
**[(https://github.com/sv-evdokimova)]**
