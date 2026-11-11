from pathlib import Path
import json
import pandas as pd
import folium
from branca.element import Element

# -----------------------------
# 1. Paths and initial data
# -----------------------------
DATA_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/maps")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(
    DATA_DIR / "air_quality_long_geo.csv",
    parse_dates=["date"]
)

POLLUTANTS = ["PM2.5", "PM10", "NO2"]

SEASONS = {
    "winter": "Winter",
    "spring": "Spring",
    "summer": "Summer",
    "autumn": "Autumn"
}

# -----------------------------
# 2. Preparing data
# -----------------------------
# We keep only the rows with measurements and coordinates.
analysis = df[
    df["pollutant"].isin(POLLUTANTS)
    & df["value"].notna()
    & df["lat"].notna()
    & df["lon"].notna()
    & df["season"].isin(SEASONS)
].copy()

# The average value for the season for each station.
station_season = (
    analysis.groupby(
        ["station", "city", "lat", "lon",
         "pollutant", "season"],
        as_index=False
    )["value"].mean()
)

# One color scale for each pollutant.
# It is the same for all four seasons.
ranges = {}

for pollutant in POLLUTANTS:
    values = station_season.loc[
        station_season["pollutant"] == pollutant,
        "value"
    ]

    if values.empty:
        raise ValueError(f"Нет данных для {pollutant}")

    vmin = float(values.min())
    vmax = float(values.max())

    if vmin == vmax:
        vmax = vmin + 1

    ranges[pollutant] = (vmin, vmax)

# -----------------------------
# 3. Color function
# -----------------------------
COLORS = [
    "#ffffb2",
    "#fecc5c",
    "#fd8d3c",
    "#f03b20",
    "#bd0026"
]

def get_color(value, vmin, vmax):
    # Переводим значение в интервал 0...1
    ratio = (value - vmin) / (vmax - vmin)
    ratio = max(0, min(1, ratio))

    index = min(int(ratio * len(COLORS)), len(COLORS) - 1)
    return COLORS[index]

# -----------------------------
# 4. Creating a basic map
# -----------------------------
m = folium.Map(
    location=[41.65, 44.90],
    zoom_start=10,
    tiles="OpenStreetMap",
    control_scale=True
)

layer_info = {}

# -----------------------------
# 5. Creating 12 layers
# -----------------------------
layers = {}
for pollutant in POLLUTANTS:
    for season, season_ru in SEASONS.items():

        layer_name = f"{pollutant} | {season_ru}"

        # Показываем только первый слой при открытии
        is_default = (
            pollutant == "PM2.5"
            and season == "winter"
        )

        layer = folium.FeatureGroup(
            name=layer_name,
            show=is_default
        )

        subset = station_season[
            (station_season["pollutant"] == pollutant)
            & (station_season["season"] == season)
        ]

        vmin, vmax = ranges[pollutant]

        for _, row in subset.iterrows():
            color = get_color(row["value"], vmin, vmax)

            popup_html = (
    f"<b>Station:</b> {row['station']}<br>"
    f"<b>City:</b> {row['city']}<br>"
    f"<b>Pollutant:</b> {pollutant}<br>"
    f"<b>Season:</b> {season_ru}<br>"
    f"<b>Mean concentration:</b> {row['value']:.2f} µg/m³"
)

            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=10,
                color="#333333",
                weight=1,
                fill=True,
                fill_color=color,
                fill_opacity=0.9,
                popup=folium.Popup(
                    popup_html,
                    max_width=250
                ),
                tooltip=(
                    f"{row['station']}: "
                    f"{row['value']:.2f} µg/m³"
                )
            ).add_to(layer)

        layer.add_to(m)
        layers[layer_name] = layer


        layer_info[layer.get_name()] = {
            "pollutant": pollutant,
            "season": season_ru,
            "vmin": vmin,
            "vmax": vmax
        }


# -----------------------------
# 7. Legend with a dynamic signature
# -----------------------------
# Создаём HTML-элемент легенды
legend_html = """
<div id="aq-legend" style="
    position: fixed;
    bottom: 25px;
    right: 25px;
    z-index: 9999;
    background: white;
    padding: 14px 16px;
    border: 1px solid #aaa;
    border-radius: 8px;
    box-shadow: 0 2px 8px #0003;
    font-family: Arial, sans-serif;
    font-size: 13px;
    min-width: 220px;
">
    <div id="aq-title"
         style="font-weight: bold; margin-bottom: 8px;">
        PM2.5 | Winter
    </div>

    <div style="
        height: 14px;
        border-radius: 4px;
        background: linear-gradient(
            to right,
            #ffffb2,
            #fecc5c,
            #fd8d3c,
            #f03b20,
            #bd0026
        );
    "></div>

    <div style="
        display: flex;
        justify-content: space-between;
        margin-top: 5px;
    ">
        <span id="aq-min"></span>
        <span id="aq-max"></span>
    </div>

    <div style="margin-top: 7px; color: #555;">
    Average concentration, µg/m³
    </div>
</div>
"""

m.get_root().html.add_child(Element(legend_html))





# -----------------------------
# 8. Two drop‑down lists + legend
# -----------------------------
from branca.element import MacroElement, Template

class AirQualityControls(MacroElement):
    def __init__(self, layer_info):
        super().__init__()
        self._name = "AirQualityControls"

        self.layer_info = layer_info

        # We explicitly pass JavaScript references to Folium objects.
    #They will be available after the map is created.
        self.layer_names = list(layer_info.keys())

        self._template = Template("""
        {% macro html(this, kwargs) %}
        <div style="
            position: fixed;
            top: 15px;
            right: 15px;
            z-index: 9999;
            background: white;
            padding: 14px;
            border-radius: 8px;
            box-shadow: 0 2px 8px #0003;
            font-family: Arial, sans-serif;
            width: 190px;
        ">
            <b>Air Quality Monitoring</b>

            <div style="margin-top: 12px;">
                <label for="aq-pollutant">Pollutant</label>
                <select id="aq-pollutant"
                        style="width:100%; margin-top:5px;">
                    <option value="PM2.5">PM2.5</option>
                    <option value="PM10">PM10</option>
                    <option value="NO2">NO₂</option>
                </select>
            </div>

            <div style="margin-top: 12px;">
        <label for="aq-season">Season</label>
        <select id="aq-season"
                style="width:100%; margin-top:5px;">
            <option value="Winter">Winter</option>
            <option value="Spring">Spring</option>
            <option value="Summer">Summer</option>
            <option value="Autumn">Autumn</option>
        </select>
    </div>
</div>
        {% endmacro %}

        {% macro script(this, kwargs) %}
        const aqMap = {{ this._parent.get_name() }};

        const aqLayers = {
            {% for name, info in this.layer_info.items() %}
            "{{ name }}": {
                layer: {{ name }},
                pollutant: {{ info.pollutant | tojson }},
                season: {{ info.season | tojson }},
                vmin: {{ info.vmin }},
                vmax: {{ info.vmax }}
            },
            {% endfor %}
        };

        function updateAirQualityMap() {
            const pollutant =
                document.getElementById("aq-pollutant").value;

            const season =
                document.getElementById("aq-season").value;

            for (const info of Object.values(aqLayers)) {

                const selected =
                    info.pollutant === pollutant &&
                    info.season === season;

                if (selected) {
                    if (!aqMap.hasLayer(info.layer)) {
                        aqMap.addLayer(info.layer);
                    }

                    document.getElementById("aq-title").textContent =
                        pollutant + " | " + season;

                    document.getElementById("aq-min").textContent =
                        info.vmin.toFixed(1);

                    document.getElementById("aq-max").textContent =
                        info.vmax.toFixed(1);

                } else {
                    if (aqMap.hasLayer(info.layer)) {
                        aqMap.removeLayer(info.layer);
                    }
                }
            }
        }

        document.getElementById("aq-pollutant")
            .addEventListener("change", updateAirQualityMap);

        document.getElementById("aq-season")
            .addEventListener("change", updateAirQualityMap);

        updateAirQualityMap();
        {% endmacro %}
        """)

AirQualityControls(layer_info).add_to(m)

# -----------------------------
# 9. Saving map
# -----------------------------
output_file = OUTPUT_DIR / "air_quality_seasonal_map.html"

m.save(str(output_file))

print("Карта сохранена:")
print(output_file.resolve())
print("Всего слоёв:", len(layer_info))
print("Станций с координатами:",
        station_season["station"].nunique())
