from .api import call_endpoint, EndpointException
from .logging import configure_logger
from .helpers import output_endpoint_error
import os


def import_station_locations(config):
    logger = configure_logger()

    if config["import_station_locations"] == "yes":
        try:
            logger.info("Importing stations and station locations.")
            call_endpoint(
                "POST",
                "import_station_locations",
                {"file_name": os.path.basename(config["weather_station_file"])},
            )
            logger.info("Stations and station locations imported.")
        except EndpointException as e:
            output_endpoint_error(str(e))
            print("Importing station and locations failed, exiting the app...")
            exit(1)
        except Exception as e:
            print(str(e))
            raise e
    else:
        logger.info("Importing stations and locations skipped...")


def import_weather_files(config, historical_names, projected_names):
    import_station_locations(config)

    logger = configure_logger()
    if config["import_weather_files_enabled"] == "yes":
        logger.info("Importing weather data.")
        try:
            logger.info("Importing historical files.")
            unique_historical_names = historical_names.copy()
            unique_historical_names = list(set(unique_historical_names))
            for historical_file_name in unique_historical_names:
                logger.info(f"Importing historical file {historical_file_name}.")
                import_historical_file(historical_file_name)
            logger.info("Historical files imported.")

            unique_projected_names = projected_names.copy()
            unique_projected_names = list(set(unique_projected_names))
            logger.info("Importing projected files and load profiles.")
            for projected_file_name in unique_projected_names:
                logger.info(f"Importing projected file {projected_file_name}.")
                import_projected_file(projected_file_name)
                import_load_profiles(
                    config,
                    projected_file_name,
                    os.path.basename(config["load_folder_name"]),
                )
            logger.info("Projected files imported.")
        except EndpointException as e:
            output_endpoint_error(str(e))
            print("Importing weather data failed, exiting the app...")
            exit(1)
        except Exception as e:
            print(str(e))
            raise e
    else:
        logger.info("Importing weather data skipped...")


def import_historical_file(file_name):
    logger = configure_logger()
    call_endpoint("POST", "register_file", {"file_name": file_name})
    logger.info("Registered " + file_name)
    call_endpoint("POST", "import_historical", {"file_name": file_name})
    logger.info("Imported " + file_name)


def import_projected_file(file_name):
    logger = configure_logger()
    call_endpoint("POST", "register_file", {"file_name": file_name})
    logger.info("Registered " + file_name)
    call_endpoint("POST", "import_projected", {"file_name": file_name})
    logger.info("Imported " + file_name)


def import_load_profiles(config, file_name, load_folder_name):
    logger = configure_logger()
    if config["import_load_profiles"] == "yes":
        logger.info("Importing load profiles from " + load_folder_name)
        call_endpoint(
            "POST",
            "import_load_data",
            {"file_name": file_name, "folder_name": load_folder_name},
        )
        print("Load profiles imported " + file_name)
    else:
        print("Load profiles importing skipped...")
