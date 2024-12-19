"""
Created on Wed May 25 14:06:38 2022

@author: pjma024
"""

import pandas as pd
import geopandas
import json
import math
from .logging import configure_logger


def power_system_df2json(df_final, df_weather_station, output):
    df_location = pd.merge(df_final, df_weather_station, on="station", how="left")
    new_column_names = {"lat": "latitude", "lon": "longitude"}
    df_location.rename(columns=new_column_names, inplace=True)
    df_location["description"] = None

    df_location_json = pd.DataFrame()
    df_location_json.insert(0, "description", df_location["description"])
    df_location_json.insert(
        1,
        "coordinates",
        df_location[["latitude", "longitude"]].astype(str).to_dict(orient="records"),
    )
    df_location_json.insert(
        2, "identifier", df_location.station.apply(lambda x: x.split("tation")[1])
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
    with open(output, "w") as json_file:
        json.dump(data_json, json_file, indent=4)


def aggregate_capacity(power_system_file, weather_station_file, number_of_stations):
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
    df_weather_station_all = pd.read_csv(weather_station_file)
    df_weather_station = df_weather_station_all.iloc[0:number_of_stations,]
    all_weather_stations = geopandas.GeoDataFrame(
        df_weather_station.StationName,
        geometry=geopandas.points_from_xy(
            df_weather_station.lat, df_weather_station.lon
        ),
    )
    df_weather_station.insert(
        4, "station", "Station" + df_weather_station.index.astype(str)
    )
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
    df_final = (
        df.groupby(["Unit Type", "station"])["Nameplate (MW)"].sum().reset_index()
    )
    return df_final, df_weather_station


def risk_model_csv2json(input, output):
    risks_df = pd.read_csv(input)

    df_json = pd.DataFrame()
    df_json.insert(0, "variable1_type", risks_df["variable1"])
    df_json.insert(1, "operator1", risks_df["operator1"])
    df_json.insert(2, "threshold1", risks_df["threshold1"])
    df_json.insert(
        3,
        "variable2_type",
        [i if not isinstance(i, float) else None for i in risks_df["variable2"]],
    )
    df_json.insert(
        4,
        "operator2",
        [i if not isinstance(i, float) else None for i in risks_df["operator2"]],
    )
    df_json.insert(
        5,
        "threshold2",
        [str(i) if not math.isnan(i) else None for i in risks_df["threshold2"]],
    )
    df_json.insert(6, "technology", risks_df["tech"])
    df_json.insert(7, "period", 0)
    df_json.insert(8, "event", risks_df["risk"])
    df_json.insert(9, "derating", risks_df["derating"].astype(str))

    data_json = df_json.to_dict(orient="records")
    with open(output, "w") as json_file:
        json.dump(data_json, json_file, indent=1)


def create_aggregate_capacity_file(config):
    base_path = "input"
    logger = configure_logger()
    logger.info("Creating aggregate capacity file.")
    df_final, df_weather_station = aggregate_capacity(
        f"{config['power_systems_file']}",
        f"{base_path}/locations/{config['weather_station_file']}",
        config["weather_stations_in_screening"],
    )
    df_final.to_csv(config["aggregate_capacity_file"], index=False)
    logger.info(
        f"Aggregate capacity file saved to: {config['aggregate_capacity_file']}"
    )
    return df_final, df_weather_station


def convert_power_systems(df_final, df_weather_station):
    logger = configure_logger()
    power_systems_json = "input/power_systems/ps-demo-input.json"
    logger.info("Converting power systems to json")
    power_system_df2json(df_final, df_weather_station, power_systems_json)
    logger.info(f"Power systems json file saved to: {power_systems_json}")
    return power_systems_json


def convert_risk_models(config):
    logger = configure_logger()
    risk_models_json = "input/risk_models/rm-demo-input.json"
    logger.info("Converting risk models to json")
    risk_model_csv2json(config["risk_model_file"], risk_models_json)
    logger.info(f"Risk model json file saved to: {risk_models_json}")
    return risk_models_json
