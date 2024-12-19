# -*- coding: utf-8 -*-
"""
Created on Wed May 25 14:06:38 2022

@author: pjma024
"""

import pandas as pd
import geopandas
import json
import sys

with open("config.json", "r") as file:
    config = json.load(file)
# weather_stations = int(sys.argv[1])
weather_stations = config["weather_stations_in_screening"]
# power_system = pd.read_excel(r"PowerSystemData.xlsx", sheet_name= '1_Gen')
power_system_file = sys.argv[1]
power_system = pd.read_csv(power_system_file)
pwr_sys = power_system[
    [
        "Asset ID",
        "Generator Shortname",
        "Operational Date",
        "Retirement Date",
        "Unit Type",
        "State",
        "Latitude",
        "Longitude",
        "Nameplate (MW)",
    ]
]
pwr_sys.groupby(["Unit Type"])
weather_station_file = sys.argv[2]
df_weather_station_all = pd.read_csv(weather_station_file)
df_weather_station = df_weather_station_all.iloc[0:weather_stations,]
all_weather_stations = geopandas.GeoDataFrame(
    df_weather_station.StationName,
    geometry=geopandas.points_from_xy(df_weather_station.lat, df_weather_station.lon),
)
lat = list(df_weather_station.lat)
lon = list(df_weather_station.lon)
df_weather_station.insert(
    4, "station", "Station" + df_weather_station.index.astype(str)
)

num_allstations = len(df_weather_station.lat)

all_stations = [
    "Station_{id_sol}".format(id_sol=i) for i in range(1, num_allstations + 1)
]

all_units = geopandas.GeoDataFrame(
    pwr_sys[
        [
            "Asset ID",
            "Operational Date",
            "Retirement Date",
            "Unit Type",
            "Nameplate (MW)",
        ]
    ],
    geometry=geopandas.points_from_xy(pwr_sys["Latitude"], pwr_sys["Longitude"]),
)
# Do the geodata for all units and find the closest weather station

all_units["station"] = all_units["geometry"].apply(
    lambda x: [
        "Station" + str(i)
        for i, j in enumerate(all_weather_stations["geometry"].distance(x))
        if j == min(all_weather_stations["geometry"].distance(x))
    ]
)
df_all_units = pd.DataFrame(all_units.drop(columns="geometry"))
df_all_units["station"] = df_all_units["station"].apply(lambda x: x[0])

df = df_all_units
# Retire units before 2027
# df = df[df['Retirement Date'].isna()].reset_index(drop =True)

df_final = df.groupby(["Unit Type", "station"])["Nameplate (MW)"].sum().reset_index()

df_final.to_csv(r"output/aggregated_capacity.csv", index=False)

df_location = pd.merge(df_final, df_weather_station, on="station", how="left")
new_column_names = {"lat": "latitude", "lon": "longitude"}
df_location.rename(columns=new_column_names, inplace=True)
df_location["description"] = str(None)

df_location_json = pd.DataFrame()
df_location_json.insert(0, "description", df_location["description"])
df_location_json.insert(
    1,
    "coordinates",
    df_location[["latitude", "longitude"]].astype(str).to_dict(orient="records"),
)
df_location_json.insert(
    2, "identifiyer", df_location.station.apply(lambda x: x.split("tation")[1])
)

df_json = pd.DataFrame()
df_json.insert(0, "short_name", df_final["Unit Type"] + "_" + df_final["station"])
df_json.insert(1, "long_name", df_final["Unit Type"] + "_" + df_final["station"])
df_json.insert(2, "station", df_final["station"])
df_json.insert(3, "location", df_location_json.to_dict(orient="records"))
df_json.insert(4, "unit_id", df_final.index.astype(str))
df_json.insert(5, "capacity", df_final["Nameplate (MW)"].astype(str))
df_json.insert(6, "resource_type", "")
df_json.insert(7, "technology", df_final["Unit Type"])

data_json = df_json.to_dict(orient="records")
line_to_add = "power_system = "
with open("output/power_system.py", "w") as file:
    file.write(line_to_add)
with open("output/power_system.py", "a") as json_file:
    json.dump(data_json, json_file, indent=4)
