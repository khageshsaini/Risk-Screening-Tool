import shutil
from .logging import configure_logger
from .api import call_endpoint


def copy_file(src_file, dst_file):
    shutil.copy(src_file, dst_file)


def copy_dir(src_dir, dst_dir):
    shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)


def sync_files(config):
    logger = configure_logger()
    if config["sync_files_enabled"] == "yes":
        logger.info(
            f"Syncing files enabled, type set to {config['sync_type']}, starting sync..."
        )
        if config["sync_type"] == "local":
            sync_files_local(config)
        else:
            sync_files_remote(config)
    else:
        logger.info("Syncing files disabled, skipping...")


def sync_files_remote(config):
    logger = configure_logger()
    logger.info("Asking backend to sync the files from remote share...")
    call_endpoint(
        "POST",
        "sync_files",
        {
            "src_historical": config["src_historical"],
            "src_predictive": config["src_predictive"],
            "weather_station_file": config["weather_station_file"],
            "load_folder_name": config["load_folder_name"],
        },
    )
    logger.info("Done syncing remote share files...")


def sync_files_local(config):
    logger = configure_logger()
    base_path = "input"

    source = f"{base_path}/nc_files/{config['src_historical']}"
    logger.info(
        f"Copying historical nc file {source} to backend target: {config['src_historical_target']}"
    )
    copy_file(source, config["src_historical_target"])
    logger.info("Historical file transferred.")

    source = f"{base_path}/nc_files/{config['src_predictive']}"
    logger.info(
        f"Copying predictive nc file {source} to backend target: {config['src_predictive_target']}"
    )
    copy_file(source, config["src_predictive_target"])
    logger.info("Predictive file transferred.")

    source = f"{base_path}/locations/{config['weather_station_file']}"
    logger.info(
        f"Copying stations and locations file {source} to backend target: {config['weather_station_file_target']}"
    )
    copy_file(source, config["weather_station_file_target"])
    logger.info("Stations and locations file transferred.")

    source = f"{base_path}/load_profiles/{config['load_folder_name']}"
    logger.info(
        f"Copying load profiles from {source} to backend target: {config['load_folder_name_target']}"
    )
    copy_dir(source, config["load_folder_name_target"])
    logger.info("Load profiles transferred.")
