# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# IMPORT
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# built-in
from pathlib import Path
from typing import Any
import pickle
import datetime

# 3rd party
import pandas as pd

# own
from preprocessing import helpers

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# FUNCTIONS
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def read_xlsx(xlsx_file: Path) -> dict[any,pd.DataFrame]:
    """
    - Reads the scenario-data from the excelfile.
    - Stores each excel-sheet as a dataframe in the dictionary with the sheet-name as key.
    """

    # Read all sheets in dictionary
    data = pd.read_excel(xlsx_file, sheet_name=None)

    return data

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def remove_stuff(data: dict[any,pd.DataFrame]) -> dict[any,pd.DataFrame]:
    """
    - Remove data that is not supposed to be there (due to notes and dummy rows in excel...)
    """

    # SIM_SETTINGS
    # remove explanation-column
    data["sim_settings"] = data["sim_settings"].drop(columns=["Simulationseinstellungen"])
    # get column-names
    colnames = data["sim_settings"].iloc[0].to_list()
    # remove unnecessary rows and reset index
    data["sim_settings"] = data["sim_settings"].iloc[1:].reset_index(drop=True)
    # set column-names
    data["sim_settings"].columns = colnames

    # WHEREABOUTS, TRANSPORTS, PEOPLE, MATERIALS
    sheet_names = ["whereabouts","transports","people","materials"]
    for sheet_name in sheet_names:
        # get column-names
        colnames = data[sheet_name].iloc[1].to_list()
        # drop unncessary rows and reset index
        data[sheet_name] = data[sheet_name].iloc[2:].reset_index(drop=True)
        # set column-names
        data[sheet_name].columns = colnames

    # DIMA (hint: acces dima with command "data["dima"].loc["B0","B12"]" (row,column))
    # set index
    data["dima"] = data["dima"].set_index("Distanzmatrix / DiMa")
    # get column-names
    colnames = data["dima"].iloc[0].to_list()
    # remove unnecessary rows
    data["dima"] = data["dima"].iloc[1:]
    # rename columns
    data["dima"].columns = colnames

    return data

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def adjust_data(data):
    """
    - adjust all the data (put in dataframes, formatting values, ...)
    """

    # SIM_SETTINGS
    # convert pd.dataframe to dictionary
    sim_settings = dict()
    for setting in data["sim_settings"].to_dict('records'):
        sim_settings[setting["Parameter"]] = setting["Wert"]
    # Combine sim_startdate and sim_starttime
    sim_settings["sim_startdatetime"] = datetime.datetime(year=sim_settings["sim_startdate"].year,
                                                          month=sim_settings["sim_startdate"].month,
                                                          day=sim_settings["sim_startdate"].day,
                                                          hour=sim_settings["sim_starttime"].hour,
                                                          minute=sim_settings["sim_starttime"].minute,
                                                          second=sim_settings["sim_starttime"].second)
    sim_settings["sim_enddatetime"] = datetime.datetime(year=sim_settings["sim_enddate"].year,
                                                        month=sim_settings["sim_enddate"].month,
                                                        day=sim_settings["sim_enddate"].day,
                                                        hour=sim_settings["sim_endtime"].hour,
                                                        minute=sim_settings["sim_endtime"].minute,
                                                        second=sim_settings["sim_endtime"].second)
    # these settings are no longer needed -> delete
    del sim_settings["sim_startdate"]
    del sim_settings["sim_starttime"]
    del sim_settings["sim_enddate"]
    del sim_settings["sim_endtime"]

    # replace dataframe with dictionary
    data["sim_settings"] = sim_settings

    # WHEREABOUTS
    # remove time from datetime element
    data["whereabouts"]["w_from_date"] = data["whereabouts"]["w_from_date"].apply(lambda x: x.date())
    # remove time from datetime element
    data["whereabouts"]["w_until_date"] = data["whereabouts"]["w_until_date"].apply(lambda x: x.date())
    # make sure it's a float
    data["whereabouts"]["w_capacity"] = data["whereabouts"]["w_capacity"].apply(lambda x: float(x))

    # PEOPLE
    # convert "None" to None. If there are entries, adjustments need to be defined...
    data["people"]["p_additionaltransports"] = data["people"]["p_additionaltransports"].apply(lambda x: None if (x == "None") else x)
    # remove time from datetime element
    data["people"]["p_missionstartdate"] = data["people"]["p_missionstartdate"].apply(lambda x: x.date())
    # remove time from datetime element
    data["people"]["p_missionenddate"] = data["people"]["p_missionenddate"].apply(lambda x: x.date())
    # convert "None" to None. If there are entries, adjustments need to be defined...
    data["people"]["p_departureloc"] = data["people"]["p_departureloc"].apply(lambda x: None if (x == "None") else x)
    # convert "None" to None. If there are entries, adjustments need to be defined...
    data["people"]["p_departuretime"] = data["people"]["p_departuretime"].apply(lambda x: None if (x == "None") else x)

    # TODO: further adjustments needed when more data available...

    # MATERIALS
    # for the time being there are no materials...
    # TODO: add when needed...

    # TRANSPORTS
    # remove time from datetime element
    data["transports"]["t_from_date"] = data["transports"]["t_from_date"].apply(lambda x: x.date())
    # remove time from datetime element
    data["transports"]["t_until_date"] = data["transports"]["t_until_date"].apply(lambda x: x.date())
    # make sure it's a float
    data["transports"]["t_capacity"] = data["transports"]["t_capacity"].apply(lambda x: float(x))
    # remove all spaces in string and convert to lower letters only
    data["transports"]["t_objects"] = data["transports"]["t_objects"].apply(lambda x: x.replace(" ", "").lower())
    # remove all spaces in string and convert to capital letters only
    data["transports"]["t_connections"] = data["transports"]["t_connections"].apply(lambda x: x.replace(" ", "").upper())

    # DIMA
    # seems to be alright so far...

    return data

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def create_transportation_requests(data):
    """
    This function creates a dataframe with all the transportation requests in it.
    """

    # create empty dataframe with columns
    df_transportationrequests = pd.DataFrame(columns=["tr_id","tr_entityname","tr_startdatetime","tr_startloc","tr_endloc","tr_route","tr_behavior"])

    # PEOPLE
    tr_id = 0
    for index,row in data["people"].iterrows():

        # 1) FIRST TRANSPORTATION-REQUEST OF ENTITY
        tr = dict()
        tr["tr_id"] = tr_id
        tr["tr_entityname"] = row["p_name"]
        tr["tr_startdatetime"] = datetime.datetime(year=row["p_missionstartdate"].year,
                                                   month=row["p_missionstartdate"].month,
                                                   day=row["p_missionstartdate"].day,
                                                   hour=row["p_arrivaltime"].hour,
                                                   minute=row["p_arrivaltime"].minute,
                                                   second=row["p_arrivaltime"].second)
        tr["tr_startloc"] = row["p_arrivalloc"]
        tr["tr_endloc"] = row["p_missionloc"]
        # TODO: Define route from startloc to endloc => When to define route? Preprocessing vs. during simulation?
        tr["tr_route"] = "TBD"
        tr["tr_behavior"] = "disappear"
        # add transportation-request to dataframe with all transportation-requests
        df_transportationrequests = pd.concat([df_transportationrequests, pd.DataFrame.from_records([tr])])
        # increase id
        tr_id += 1

        # 2) OTHER TRANSPORTATION-REQUESTS OF THE SAME ENTITY... (LUNCH, EVENING, TOILET, ...)
        # TODO: Much more to come!

        # last transportation-request of enitiy (disposal/leaving forever)
        # daily TRs after arrival and before departure
        # additional daily transportation-requests
        # => expected behavior-types: work(people), store(material), leave(both)

    # MATERIALS

    # TODO: Add when needed...

    # add transportation-requests to data
    data["transportationrequests"] = df_transportationrequests

    return data

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def organize_data(data: dict[Any]) -> dict[str,list[Any]]:
    """
    - Create Pydantic-"dataobjects" from the dataframes.
    """

    # ··················································································································

    def organize_whereabouts(datadict) -> list[helpers.Whereabout]:

        # initialize lists for all whereabouts
        whereabouts = list()
        # organize data (create a dict first)
        for index,row in datadict["whereabouts"].iterrows():
            whereabout = dict()
            whereabout["id"] = int(row["w_id"])
            whereabout["description"] = str(row["w_description"])
            whereabout["name"] = str(row["w_name"])
            whereabout["capacity"] = float(row["w_capacity"])
            whereabout["queues"] = helpers.get_whereabout_queues(whereabout_name=whereabout["name"],
                                                                 df_transports=datadict["transports"])
            whereabout["from_datetime"] = helpers.combine_date_and_time(my_date=row["w_from_date"],
                                                                        my_time=row["w_from_time"])
            whereabout["from_s"] = helpers.convert_time_to_seconds(sim_start=datadict["sim_settings"]["sim_startdatetime"],
                                                                   timestamp=whereabout["from_datetime"])
            whereabout["until_datetime"] = helpers.combine_date_and_time(my_date=row["w_until_date"],
                                                                         my_time=row["w_until_time"])
            whereabout["until_s"] = helpers.convert_time_to_seconds(sim_start=datadict["sim_settings"]["sim_startdatetime"],
                                                                    timestamp=whereabout["until_datetime"])
            whereabout["log"] = list()

            # create dataclass-instance from dict and add to list
            whereabouts.append(helpers.Whereabout(**whereabout))

        return whereabouts

    # ··················································································································

    def organize_transports(datadict) -> list[helpers.Transport]:

        # initialize list of all transports
        transports = list()
        # organize data (create a dict first)
        for index,row in datadict["transports"].iterrows():
            transport = dict()
            transport["id"] = int(row["t_id"])
            transport["description"] = str(row["t_description"])
            transport["name"] = str(row["t_name"])
            transport["type"] = str(row["t_type"])
            transport["from_datetime"] = helpers.combine_date_and_time(my_date=row["t_from_date"],
                                                                       my_time=row["t_from_time"])
            transport["from_s"] = helpers.convert_time_to_seconds(sim_start=datadict["sim_settings"]["sim_startdatetime"],
                                                                  timestamp=transport["from_datetime"])
            transport["until_datetime"] = helpers.combine_date_and_time(my_date=row["t_until_date"],
                                                                        my_time=row["t_until_time"])
            transport["until_s"] = helpers.convert_time_to_seconds(sim_start=datadict["sim_settings"]["sim_startdatetime"],
                                                                   timestamp=transport["until_datetime"])
            transport["allowed_to_transport"] = row["t_objects"].split(",")
            transport["on_board"] = list()
            transport["capacity"] = float(row["t_capacity"])
            transport["speed"] = float(row["t_speed"])
            transport["strategy"] = str(row["t_strategy"])
            transport["connections"] = helpers.convert_connections(row["t_connections"])
            transport["queues"] = row["t_queues"].split(",")
            transport["fixload_time"] = int(row["t_fixload"])
            transport["varload_time"] = int(row["t_varload"])
            transport["fixunload_time"] = int(row["t_fixunload"])
            transport["varunload_time"] = int(row["t_varunload"])
            transport["idle"] = str(row["t_idle"])
            transport["log"] = list()

            # create dataclass-instance from dict and add to list
            transports.append(helpers.Transport(**transport))

        return transports

    # ··················································································································

    def organize_entities(datadict):

        # PEOPLE

        # initialize list of all entities
        entities = list()

        # organize data (create a dict first)
        for index,row in datadict["people"].iterrows():
            entity = dict()
            entity["id"] = int(row["p_id"])
            entity["description"] = str(row["p_description"])
            entity["name"] = str(row["p_name"])
            entity["type"] = "people"
            entity["quantity"] = float(row["p_quantity"])
            entity["current_wa"] = None
            entity["current_behavior"] = None
            entity["active_tr"] = None
            entity["open_tr"] = helpers.get_tr_from_entity(name=entity["name"],trs=datadict["transportationrequests"])
            entity["closed_tr"] = list()
            entity["log"] = list()

            # create dataclass-instance from dict and add to list
            entities.append(helpers.Entity(**entity))

        # MATERIALS

        for index,row in datadict["materials"].iterrows():
            ...
            # TODO: Add when needed...

        return entities

    # ··················································································································

    def organize_transportationrequests(datadict):

        # initialize list of all transportation-requests
        transportation_requests = list()
        # organize data (create a dict first)
        for index,row in datadict["transportationrequests"].iterrows():
            transportation_request = dict()
            transportation_request["id"] = int(row["tr_id"])
            transportation_request["entity_name"] = str(row["tr_entityname"])
            transportation_request["start_datetime"] = row["tr_startdatetime"]
            transportation_request["start_s"] = helpers.convert_time_to_seconds(sim_start=datadict["sim_settings"]["sim_startdatetime"],
                                                                                timestamp=transportation_request["start_datetime"])
            transportation_request["entity_type"] = "people" if ("P" in row["tr_entityname"]) else "materials"
            transportation_request["start_wa"] = str(row["tr_startloc"])
            transportation_request["end_wa"] = str(row["tr_endloc"])
            # TODO: define route... when?
            transportation_request["route"] = list()
            transportation_request["behavior"] = str(row["tr_behavior"])

            # create dataclass-instance from dict and add to list
            transportation_requests.append(helpers.TransportationRequest(**transportation_request))

        # sort transportation-requests to start-time in seconds
        transportation_requests.sort(key=lambda x: x.start_s)

        return transportation_requests

    # ··················································································································

    def organize_sim_settings(datadict):

        sim_settings = dict()
        sim_settings["start_datetime"] = datadict["sim_settings"]["sim_startdatetime"]
        sim_settings["start_s"] = helpers.convert_time_to_seconds(sim_start=datadict["sim_settings"]["sim_startdatetime"],
                                                                  timestamp=sim_settings["start_datetime"])
        sim_settings["end_datetime"] = datadict["sim_settings"]["sim_enddatetime"]
        sim_settings["end_s"] = helpers.convert_time_to_seconds(sim_start=datadict["sim_settings"]["sim_startdatetime"],
                                                                timestamp=sim_settings["end_datetime"])

        return sim_settings

    # ··················································································································

    # MAIN (ORGANIZE_DATA)

    organized_data = dict()
    organized_data["whereabouts"] = organize_whereabouts(data)
    organized_data["transports"] = organize_transports(data)
    organized_data["entities"] = organize_entities(data)
    organized_data["transportation_requests"] = organize_transportationrequests(data)
    organized_data["dima"] = data["dima"]
    organized_data["sim_settings"] = organize_sim_settings(data)

    return organized_data

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def save_data(data, pickle_file):
    """
    - Save the data as a pickle-file at given path.
    """

    with pickle_file.open("wb") as f:
        pickle.dump(data,f)

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# MAIN
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def run(xlsx_file):
    """
    Preprocess the data:
    - read data from excel
    - tidy/remove unnecessary data
    - reformat data
    - create transportation-requests
    - organize as objects
    - save data
    """

    data = read_xlsx(xlsx_file=xlsx_file)
    data = remove_stuff(data=data)
    data = adjust_data(data=data)
    data = create_transportation_requests(data=data)
    data = organize_data(data=data)
    return data
    # save_data(data=data,pickle_file=pickle_file)

    # TODO: Add Data Validation somewhere...
