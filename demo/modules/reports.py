import json
from .api import call_endpoint
from .reports_export import save_csv, save_report, save_split_results
import time
from .logging import configure_logger
from .helpers import get_output_file_name

def create_report(
    project_name,
    weather_files,
    year,
    e_interval,
    e_gap,
    e_perc,
    e_thres,
    start_date,
    end_date,
):
    logger = configure_logger()
    logger.info(f"Calculating average risk split report for project: {project_name}")
    start_time = time.time()
    logger.info(
        f"Report is created for weather files ({weather_files}), "
        f"year ({year}), interval ({e_interval}), gap ({e_gap}), "
        f"top percent ({e_perc}), threshold ({e_thres}), "
        f"start date ({start_date}), end date ({end_date})."
    )
    calculate_avg_risk_split(
        project_name,
        weather_files,
        year,
        e_gap,
        e_perc,
        e_interval,
        e_thres,
        start_date,
        end_date,
    )
    end_time = time.time() - start_time
    print("Calculating average risk report took: " + str(end_time))

    logger.info(f"Creating average risk split report for project: {project_name}")
    report_name = get_split_risk_report(
        project_name, weather_files, year, e_gap, e_perc, e_interval, e_thres, start_date, end_date
    )
    end_time = time.time() - start_time
    print("Creating average risk report took: " + str(end_time))

    logger.info(f"Downloading risk split report for project: {project_name}")
    download_risk_report(report_name)
    logger.info(f"Risk split report for project {project_name} downloaded successfuly.")


def calculate_avg_risk(project_name, weather_files, year, gap, interval_l, top_perc):
    response = call_endpoint(
        "POST",
        "calculate_average_risk",
        {
            "project_name": project_name,
            "files": weather_files,
            "weather_year": year,
            "day_gap": gap,
            "day_increment": interval_l,
            "threshold": 0,
            "percentage": top_perc,
        },
    )
    save_csv(project_name, "calculate_average_risk", response.text)


def calculate_avg_risk_split(
    project_name,
    weather_files,
    year,
    gap,
    top_perc,
    interval_l,
    threshold_mw,
    start_date,
    end_date,
):
    response = call_endpoint(
        "POST",
        "calculate_average_risk_split",
        {
            "project_name": project_name,
            "files": weather_files,
            "weather_year": year,
            "day_gap": gap,
            "day_increment": interval_l,
            "threshold": threshold_mw,
            "percentage": top_perc,
            "start_date": start_date,
            "end_date": end_date,
        },
    )
    save_split_results(project_name, "calculate_average_risk_split", response.text)


def get_split_risk_report(
    project_name,
    weather_files,
    year,
    gap,
    top_perc,
    interval_l,
    threshold_mw,
    start_date,
    end_date,
):
    response = call_endpoint(
        "POST",
        "export_average_risk_result_split",
        {
            "project_name": project_name,
            "files": weather_files,
            "weather_year": year,
            "day_gap": gap,
            "day_increment": interval_l,
            "threshold": threshold_mw,
            "percentage": top_perc,
            "start_date": start_date,
            "end_date": end_date,
        },
    )
    return json.loads(response.text)["data"]["file_name"]


def reports_project(project_name):
    save_report("get_projects", project_name, "GET")
    save_report(
        "get_project_details", project_name, "POST", {"project_name": project_name}
    )


def reports_summary(project_name):
    save_report(
        "get_event_summary_for_stations",
        project_name,
        "POST",
        {"project_name": project_name},
    )
    save_report(
        "get_event_summary_for_technologies",
        project_name,
        "POST",
        {"project_name": project_name},
    )
    save_report(
        "get_event_summary_for_risk_models",
        project_name,
        "POST",
        {"project_name": project_name},
    )


def reports_event_tags(
    project_name, risk_model_name, station_name, tech_name, start_date, end_date
):
    save_report(
        "get_event_tags_for_station",
        project_name,
        "POST",
        {"project_name": project_name, "station_name": station_name},
    )
    save_report(
        "get_event_tags_for_technology",
        project_name,
        "POST",
        {"project_name": project_name, "technology_name": tech_name},
    )
    save_report(
        "get_event_tags_by_date",
        project_name,
        "POST",
        {"project_name": project_name, "start_date": start_date, "end_date": end_date},
    )
    save_report(
        "get_event_tags_for_risk_model",
        project_name,
        "POST",
        {
            "project_name": project_name,
            "event": risk_model_name,
            "technology": tech_name,
        },
    )


def reports_weather_data(project_name, station_name, start_date, end_date):
    save_report(
        "get_weather_data",
        project_name,
        "POST",
        {"station_name": station_name, "start_date": start_date, "end_date": end_date},
    )


def download_risk_report(report_name):
    response = call_endpoint("GET", "download_xlsx_report/" + report_name)
    report_name = get_output_file_name(report_name[:-(24+37)], "download_risk_report", ".xlsx")
    with open(report_name, "wb") as f:
        f.write(response.content)
