from datetime import datetime
import os
import yaml
import json
import uuid
from .logging import configure_logger


def remove_whitespaces(s):
    return "".join(s.split())


def get_output_file_name(project_name, endpoint_name, extension):
    output_folder_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        f"../output/{remove_whitespaces(project_name)}",
    )
    os.makedirs(output_folder_path, exist_ok=True)
    current_dt = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    output_file_name = remove_whitespaces(endpoint_name) + "_" + current_dt + extension

    # Construct the full file path
    full_file_path = os.path.join(output_folder_path, output_file_name)

    return full_file_path


def load_config(config_file):
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config


# update config so it is backwards compatible with existing code
# also it merges config settings from system config to config object
def update_config(config, sysconfig):
    props = [
        "clean_database",
        "split_weather_data_enabled",
        "import_weather_files_enabled",
        "import_station_locations",
        "import_load_profiles",
        "generate_events"
        ]
    for prop in props:
        if config["reset_all"] == "yes":
            config[prop] = "yes"
        elif config["reset_all"] == "sys":
            config[prop] = sysconfig[prop]
        else:
            config[prop] = "no"

    # local sync and system auth
    props = [
        "src_predictive_target",
        "src_historical_target",
        "weather_station_file_target",
        "load_folder_name_target",
        "username",
        "password",
        "generate_events",
        "host",
        "port",
        "protocol"
        ]
    for prop in props:
        config[prop] = sysconfig[prop]
        
    return config


def load_json(file_name):
    with open(file_name, "r") as file:
        data = json.load(file)
    return data


def load_file(file_name):
    with open(file_name, "r") as file:
        file_content = file.read()
    return file_content


def output_endpoint_error(json_string):
    logger = configure_logger()
    if is_valid_json(json_string):
        logger.info(json_string)
    else:
        print_invalid_json(json_string)


def print_invalid_json(response):
    logger = configure_logger()
    filename = uuid.uuid4().hex
    logger.error(
        f"Response from backend is not json, please check the value in file output/{filename}.html"
    )
    write_to_file(f"output/{filename}.html", response)


def is_valid_json(my_str):
    try:
        json.loads(my_str)
    except ValueError:
        return False
    return True


def write_to_file(filename: str, content: str):
    with open(filename, "w+") as text_file:
        text_file.write(content)


def format_time(time):
    return datetime.fromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S")


def get_timestamp():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d-%H:%M:%S")
    return formatted_time
