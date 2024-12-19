import modules.auth as auth
from modules.project import process_projects
from modules.helpers import (
    load_config,
    update_config,
    load_json,
)
from modules.db import empty_db
from modules.transform import (
    create_aggregate_capacity_file,
    convert_power_systems,
    convert_risk_models
)
from modules.logging import configure_logger
from modules.transform_nc import split_nc_files
from modules.weather_files_import import import_weather_files
from modules.file_sync import sync_files

def main():
    logger = configure_logger()
    config = load_config("config.yml")
    sysconfig = load_config("sysconfig.yml")
    config = update_config(config, sysconfig)
    auth.setup_auth(config)

    empty_db(config)

    df_final, df_weather_station = create_aggregate_capacity_file(config)
    power_systems_json = convert_power_systems(df_final, df_weather_station)
    risk_models_json = convert_risk_models(config)

    logger.info("Loading power systems and risk models")
    power_systems_input = load_json(power_systems_json)
    risk_models = load_json(risk_models_json)
    logger.info("Power systems and risk models loaded.")

    sync_files(config)
    
    historical_names, projected_names = split_nc_files(config)

    import_weather_files(config, historical_names, projected_names)

    logger.info(f"Exported NC files: {historical_names}, {projected_names}")
    weather_files_list = [list(pair) for pair in zip(historical_names, projected_names)]
    logger.info(f"Weather files list: {weather_files_list}")
    power_systems = [power_systems_input[:] for _ in range(len(weather_files_list))]

    process_projects(config, weather_files_list, power_systems, risk_models)


if __name__ == "__main__":
    main()
