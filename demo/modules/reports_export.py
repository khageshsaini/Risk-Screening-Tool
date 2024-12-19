import json
import csv
from .helpers import get_output_file_name, remove_whitespaces
from .api import call_endpoint


def save_split_results(project_name, endpoint_name, data):
    tmp = json.loads(data)
    data = tmp["data"]["data"]
    year = tmp["data"]["year"]
    fixed_data = []
    for elem in data:
        for result in elem["results"]:
            fixed_data.append(
                {
                    "start": result["start"],
                    "end": result["end"],
                    "average": result["average"],
                    "model": elem["model"],
                    "scenario": elem["scenario"],
                    "year": year,
                    "report": result["report"]
                }
            )
    file_name = get_output_file_name(
        remove_whitespaces(project_name), endpoint_name, ".csv"
    )
    output_file = open(file_name, "w+")
    keys = fixed_data[0].keys()
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(fixed_data)


def save_report(endpoint_name, project_name, method, payload=None):
    response = call_endpoint(method, endpoint_name, payload)
    save_json(response.text, endpoint_name, project_name)


def save_json(data, endpoint_name, project_name):
    data_json = json.loads(data)
    file_name = get_output_file_name(project_name, endpoint_name, ".json")
    with open(file_name, "w+") as outfile:
        outfile.write(json.dumps(data_json, indent=4, sort_keys=True))
        outfile.close()
    return


def save_csv(project_name, endpoint_name, data):
    data = json.loads(data)["data"]["result"]
    file_name = get_output_file_name(
        remove_whitespaces(project_name), endpoint_name, ".csv"
    )
    output_file = open(file_name, "w+")
    keys = data[0].keys()
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(data)
