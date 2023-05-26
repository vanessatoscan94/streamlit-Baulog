# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# IMPORT
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import datetime
import pydantic

from typing import Any,Union

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# SETUP
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# CLASSES
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

class Transport(pydantic.BaseModel):

    id: int
    description: str
    name: str
    type: str
    from_datetime: datetime.datetime
    from_s: int
    until_datetime: datetime.datetime
    until_s: int
    allowed_to_transport: list[str]
    on_board: list[str]
    capacity: float
    speed: float
    strategy: str
    connections: dict[str,list[str]]
    queues: list[str]
    fixload_time: int
    varload_time: int
    fixunload_time: int
    varunload_time: int
    idle: str
    log: list

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

class Entity(pydantic.BaseModel):

    id: int
    description: str
    name: str
    type: str
    quantity: float
    current_wa: Union[None,str]
    current_behavior: Union[None,str]
    active_tr: Union[None,int]
    open_tr: list[int]
    closed_tr: list[int]
    log: list

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

class Whereabout(pydantic.BaseModel):

    id: int
    description: str
    name: str
    capacity: float
    queues: list[str]
    from_datetime: datetime.datetime
    from_s: int
    until_datetime: datetime.datetime
    until_s: int
    log: list

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

class TransportationRequest(pydantic.BaseModel):

    id: int
    entity_name: str
    entity_type: str
    start_datetime: datetime.datetime
    start_s: int
    start_wa: str
    end_wa: str
    route: list[Any]
    behavior: str

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# FUNCTIONS
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def get_whereabout_queues(whereabout_name,df_transports):
    """
    Function lists all queues that should be available at a specific whereabout.
    """
    queues = list()

    for index,row in df_transports.iterrows():
        if whereabout_name in row["t_connections"]:
            queues.append(row["t_name"])
    # Add queues for working (people), storing (materials), passing, etc. here...
    queues.append("work")
    queues.append("store")
    queues.append("pass")

    # TODO: Add shared queues here...
    # TODO: IDEA: vehicle only checks if its name is in the queue-name. easier for generating additional shared queues...

    return queues

# ······················································································································

def combine_date_and_time(my_date,my_time):
    """
    Function combines datetime.date and datetime.time to a datetime.datetime object.
    """

    return datetime.datetime(year=my_date.year,
                             month=my_date.month,
                             day=my_date.day,
                             hour=my_time.hour,
                             minute=my_time.minute,
                             second=my_time.second)

# ······················································································································

def convert_time_to_seconds(sim_start,timestamp):
    """
    Function converts a datetime.timestamp to the number of seconds passed since sim_start.
    """

    return int((timestamp - sim_start).total_seconds())

# ······················································································································

def convert_connections(connections):
    """
    Function creates a dict with all the connections of a specific transport (all paths).
    """

    connections = connections.split(",")
    new_connections = dict()

    for connection in connections:
        a,b = connection.split("-")

        if a not in new_connections:
            new_connections[a] = list()
        new_connections[a].append(b)

        if b not in new_connections:
            new_connections[b] = list()
        new_connections[b].append(a)

    return new_connections

# ······················································································································

def get_tr_from_entity(name,trs):
    """
    Function returns all transportation-requests that belong to one entity as a list.
    """

    return trs.loc[trs["tr_entityname"] == name, "tr_id"].to_list()

# ······················································································································
