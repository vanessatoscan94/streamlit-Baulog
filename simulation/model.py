# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# IMPORT
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# built-in
from typing import Any

# 3rd party
import simpy

# own
from simulation.source import Source
from simulation.sinks import Sink
from simulation.whereabouts import Whereabout
from simulation.transports import Elevator
from simulation.logic import Logic

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# SETUP
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# CLASSES
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

class Model:

    # ··················································································································

    def __init__(self, data: dict[Any]):

        self.env = simpy.Environment()
        self.settings = data["sim_settings"]
        self.source = Source(env=self.env,model=self,transportation_requests=data["transportation_requests"],entities=data["entities"])
        self.sink = Sink(env=self.env)
        self.whereabouts = self.__create_whereabouts(whereabouts_data=data["whereabouts"])
        self.entities = list()
        self.dima = data["dima"]
        self.transportation_requests = {transportation_request.id: transportation_request for transportation_request in data["transportation_requests"]}
        self.logic = Logic(model=self)
        self.transports = self.__create_transports(transports_data=data["transports"])

        # PROCESSES
        self.env.process(self.source.create_entities())
        for transport in self.transports:
            self.env.process(transport.transport_entities())

    # ··················································································································

    def __create_whereabouts(self,whereabouts_data):
        """
        Method creates a dict with the whereabout name as key and the whereabout-object as value.
        """

        whereabouts = dict()
        for whereabout_data in whereabouts_data:
            whereabout = Whereabout(self.env,whereabout_data)
            whereabouts[whereabout.name] = whereabout

        return whereabouts

    # ··················································································································

    def __create_transports(self,transports_data):
        """
        Method creates a list of all transports.
        """

        transports = list()
        for transport_data in transports_data:
            if transport_data.type == "Elevator":
                transports.append(Elevator(self,transport_data))
            else:
                raise NotImplementedError("So far only type Elevator available...")

        return transports

    # ··················································································································

    def run(self):
        """
        Method that runs the simulation as long as the time set in the sim-settings.
        """
        self.env.run(until=self.settings["end_s"])

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
