from .reports_export import save_report
from .api import call_endpoint, call_endpoint_silent, EndpointException
from .logging import configure_logger
import time
import traceback
from .reports import create_report
from datetime import datetime
from .helpers import get_timestamp


def create_and_prepare_project(project_name, ps, rm):
    logger = configure_logger()
    logger.info(f"Adding project: {project_name}")
    save_report("add_project", project_name, "POST", {"name": project_name})
    ps_count = len(ps)
    logger.info(
        f"Importing power systems ({ps_count} power systems) for project: {project_name}"
    )
    save_report(
        "import_power_systems",
        project_name,
        "POST",
        {"project_name": project_name, "power_systems": ps},
    )
    rm_count = len(rm)
    logger.info(
        f"Importing risk models ({rm_count} risk models) for project: {project_name}"
    )
    save_report(
        "import_risk_models",
        project_name,
        "POST",
        {"project_name": project_name, "risk_models": rm},
    )


def delete_project(project_name):
    call_endpoint_silent("POST", "delete_project", {"project_name": project_name})


def apply_risk_models(project_name, weather_files, year, start_date, end_date):
    save_report(
        "apply_risk_models",
        project_name,
        "POST",
        {
            "files": weather_files,
            "project_name": project_name,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
        },
    )


def import_load_data(file_name, folder_name):
    call_endpoint(
        "POST", "import_load_data", {"file_name": file_name, "folder_name": folder_name}
    )


def generate_project_names(config):
    scenarios = config["scenarios"]
    models = config["models"]
    file_year = list(range(config["start_year"], config["end_year"] + 1))
    target_year = config["target_year"]
    project_names = []
    for scenario in scenarios:
        for model in models:
            project_names.append(
                generate_project_name(
                    config["project_region"], model, scenario, file_year, target_year
                )
            )
    return project_names


def generate_project_name(region_name, model, scenario, file_year, target_year):
    timestamp = get_timestamp()
    return f"{region_name}_{target_year}_{model}_{scenario}_{file_year[0]}_{file_year[len(file_year) - 1]}_{timestamp}".replace(
        ":", "-"
    )


def generate_date_strings(start_year, end_year, repeat_times):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year - 1, 12, 31, 23)

    start_string = start_date.strftime("%m/%d/%Y %H:%M")
    end_string = end_date.strftime("%m/%d/%Y %H:%M")

    start_list = [start_string] * repeat_times
    end_list = [end_string] * repeat_times
    return start_list, end_list


def process_projects(config, weather_files_list, power_systems, risk_models):
    logger = configure_logger()
    project_names = generate_project_names(config)
    start_dates, end_dates = generate_date_strings(
        config["start_year"], config["end_year"], len(project_names)
    )
    delete_project_first = config["delete_project_first"]
    year = str(config["target_year"])
    event_interval = config["event_day_interval"]
    event_gap = config["event_day_overlap"]
    event_perc = config["top_events_percentage"]
    event_thres = config["threshold_MW"]
    try:
        for project_name, weather_files, start_date, end_date, power_system in zip(
            project_names, weather_files_list, start_dates, end_dates, power_systems
        ):
            logger.info(f"Processing project: {project_name}")
            if delete_project_first == "yes":
                logger.info(f"Deleting previous instance of project: {project_name}")
                try:
                    delete_project(project_name)
                except EndpointException as e:
                    error_text = str(e)
                    if "There is no project with the given name!" in error_text:
                        logger.info("Project wasn't in database, skipping deleting!")
                    else:
                        raise e
            logger.info(f"Creating project: {project_name}")
            create_and_prepare_project(project_name, power_system, risk_models)

            if config["generate_events"] == "yes":
                logger.info(f"Generating events for project: {project_name}")
                start_time = time.time()
                apply_risk_models(
                    project_name, weather_files, year, start_date, end_date
                )
                end_time = time.time() - start_time
                print("Processing events took: " + str(end_time))
            else:
                logger.info(f"Skipped generating events for project: {project_name}")

            logger.info(f"Creating reports for project: {project_name}")
            start_time = time.time()
            create_report(
                project_name,
                weather_files,
                year,
                event_interval,
                event_gap,
                event_perc,
                event_thres,
                start_date,
                end_date,
            )
            end_time = time.time() - start_time
            logger.info("Creating reports took: " + str(end_time))

            logger.info(f"Done processing project: {project_name}")
            logger.info("-" * 90)
    except EndpointException as e:
        print(str(e))
    except Exception as e:
        logger.error(traceback.format_exc())
        print(str(e))
        raise e
