# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# IMPORT
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

from pathlib import Path
from typing import Any
import pickle
import matplotlib.pyplot as plt

import pandas as pd
import json

from analytics.helpers import Entity

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# FUNCTIONS
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def load_data(scenario_file: Path, simulation_file: Path) -> tuple[dict[Any],dict[Any]]:

    # ··················································································································

    def load_model(_scenario_file: Path) -> dict[Any]:
        with _scenario_file.open("rb") as f:
            _model = pickle.load(f)
        return _model

    # ··················································································································

    def load_results(_simulation_file: Path) -> dict[Any]:
        with _simulation_file.open("rb") as f:
            _results = pickle.load(f)
        return _results

    # ··················································································································

    # MAIN

    model = load_model(scenario_file)
    results = load_results(simulation_file)

    return model,results

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def exctract_log_records(results):

    # ··················································································································

    def extract_entity_records(_results):

        records = list()

        for entity in _results["entities"]:
            record = dict()
            record["id"] = entity.id
            record["arrival_time"] = [log_entry["time"] for log_entry in entity.log if log_entry["event"] == "START" and log_entry["action"] == "LIFE"][0]
            record["departure_time"] = [log_entry["time"] for log_entry in entity.log if log_entry["event"] == "END" and log_entry["action"] == "LIFE"][0]
            record["start_whereabout"] = [log_entry["whereabout"] for log_entry in entity.log if log_entry["event"] == "START" and log_entry["action"] == "LIFE"][0]
            record["end_whereabout"] = [log_entry["whereabout"] for log_entry in entity.log if log_entry["event"] == "END" and log_entry["action"] == "LIFE"][0]
            record["start_waiting_time"] = [log_entry["time"] for log_entry in entity.log if log_entry["event"] == "START" and log_entry["action"] == "WAITING"][0]
            record["end_waiting_time"] = [log_entry["time"] for log_entry in entity.log if log_entry["event"] == "END" and log_entry["action"] == "WAITING"][0]
            record["start_transportation_time"] = [log_entry["time"] for log_entry in entity.log if log_entry["event"] == "START" and log_entry["action"] == "TRANSPORT"][0]
            record["end_transportation_time"] = [log_entry["time"] for log_entry in entity.log if log_entry["event"] == "END" and log_entry["action"] == "TRANSPORT"][0]
            record["lifetime"] = record["departure_time"] - record["arrival_time"]
            record["waiting_time"] = record["end_waiting_time"] - record["start_waiting_time"]
            record["transportation_time"] = record["end_transportation_time"] - record["start_transportation_time"]
            records.append(record)

        return records
    # ··················································································································

    def extract_transport_records(_results):
        _all_records = dict()
        for transport in _results["transports"]:
            _all_records[transport.name] = list()
            for log_entry in transport.log:
                _all_records[transport.name].append(log_entry)

        return _all_records

    # ··················································································································

    def extract_whereabout_records(_results):
        _all_records = dict()
        for whereabout in _results["whereabouts"]:
            _all_records[whereabout.name] = list()
            for log_entry in whereabout.log:
                _all_records[whereabout.name].append(log_entry)

        return _all_records

    # ··················································································································

    def extract_sink_records(_results):
        records = list()
        for log_entry in _results["sink"].log:
            records.append(log_entry)

        return records
    # ··················································································································

    # MAIN
    all_records = dict()
    all_records["entities"] = extract_entity_records(results)
    all_records["transports"] = extract_transport_records(results)
    all_records["whereabouts"] = extract_whereabout_records(results)
    all_records["sink"] = extract_sink_records(results)

    return all_records

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def analyze_records(records):

    df_entity_records = pd.DataFrame(records["entities"])
    # Create a boxplot of a column
    df_entity_records.boxplot(column='waiting_time')

    # Set the title and axis labels
    plt.title('Boxplot of my_column')
    plt.ylabel('Values')

    # Display the plot
    plt.show()

def json_export(results,export_file):

    my_json = dict()
    my_json["whereabouts"] = dict()
    my_json["entities"] = dict()
    my_json["transports"] = dict()

    for whereabout in results["whereabouts"]:
        my_json["whereabouts"][whereabout.name] = whereabout.log

    for entity in results["entities"]:
        my_json["entities"][entity.id] = entity.log

    for transport in results["transports"]:
        my_json["transports"][transport.name] = transport.log

    with open(export_file, "w") as outfile:
        json.dump(my_json,outfile)

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# MAIN
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def run(scenario_file: Path, simulation_file: Path, export_file: Path) -> None:

    model,results = load_data(scenario_file=scenario_file,simulation_file=simulation_file)
    records = exctract_log_records(results)
    # analyze_records(records)
    # calculate KPI
    # create visualizations
    # create report
    # save results
    json_export(results,export_file)

