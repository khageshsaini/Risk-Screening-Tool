import time
from .logging import configure_logger
from .helpers import output_endpoint_error
import os
from .api import call_endpoint, EndpointException


def split_nc_files(config):
    logger = configure_logger()
    if config["split_weather_data_enabled"] == "yes":
        try:
            logger.info("Splitting NC files.")
            historical_names, projected_names = split_nc_files_helper(
                config["project_region"],
                os.path.basename(config["src_predictive"]),
                os.path.basename(config["src_historical"]),
                config["scenarios"],
                config["models"],
                config["weather_stations_in_screening"],
                list(range(config["start_year"], config["end_year"])),
                config["target_year"]
            )
            logger.info("Done splitting NC files.")
        except Exception as e:
            output_endpoint_error(str(e))
            raise e
    else:
        logger.info("Splitting NC files skipped. Generating split file names...")
        historical_names, projected_names = generate_file_names(config)
    return historical_names, projected_names

def split_nc_files_helper(
    region_name, src_predictive, src_historical, scenarios, models, stations_number, file_year, target_year
):
    logger = configure_logger()
    stations = list(range(stations_number))
    historical_names = []
    projected_names = []
    try:
        for scenario in scenarios:
            for model in models:
                start = time.time()
                export_hist, export_proj = generate_file_name(region_name, model, scenario, file_year, target_year)
                historical_names.append(export_hist)
                projected_names.append(export_proj)
                logger.info(
                    f"Creating split nc files: {export_hist}, {export_proj}"
                )
                call_endpoint(
                    "POST",
                    "export_nc_files",
                    {
                        "historical_file_name": src_historical,
                        "historical_exported_file_name": export_hist,
                        "projected_file_name": src_predictive,
                        "projected_exported_file_name": export_proj,
                        "models": [model],
                        "scenarios": [scenario],
                        "stations": stations,
                        "years": file_year,
                    },
                )
            logger.info(
                export_hist
                + " | "
                + export_proj
                + " took "
                + str(time.time() - start)
                + " seconds"
            )
    except EndpointException as e:
        output_endpoint_error(str(e))
        raise e
    except Exception as e:
        output_endpoint_error(str(e))
        raise e
    return historical_names, projected_names


def generate_file_names(config):
    target_year = config["target_year"]
    scenarios = config["scenarios"]
    models = config["models"]
    file_year = list(range(config["start_year"], config["end_year"]))
    historical_names = []
    projected_names = []
    for scenario in scenarios:
        for model in models:
            export_hist, export_proj = generate_file_name(config["project_region"], model, scenario, file_year, target_year)
            historical_names.append(export_hist)
            projected_names.append(export_proj)
    return historical_names, projected_names

def generate_file_name(region_name, model, scenario, file_year, target_year):
    historical = f"{region_name}_{file_year[0]}_{file_year[len(file_year) - 1]+1}_historical.nc"
    projected = f"{region_name}_{model}_{scenario}_{file_year[0]}_{file_year[len(file_year) - 1]+1}_projected_{target_year}.nc"
    return historical, projected