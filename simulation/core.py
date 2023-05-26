# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# IMPORT
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# built-in
import pickle

# own
from simulation.model import Model
from simulation.helpers import Whereabout,Transport,Entity,TransportationRequest,Sink

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# FUNCTIONS
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def load_data(pickle_file):
    """
    Function loads the data from a pickle file and returns it as a dict.
    """

    # load data from pickle file
    with pickle_file.open("rb") as f:
        data = pickle.load(f)

    return data

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def dump_results(model, pickle_file):
    """
    Function retrieves all the results and stores it in a dict of pydantic dataclasses.
    It then dumps the results to a pickle file.
    """

    def extract_results(mdl):
        rslts = dict()
        rslts["whereabouts"] = [Whereabout.parse_obj(whereabout.__dict__) for whereabout in mdl.whereabouts.values()]
        rslts["entities"] = [Entity.parse_obj(entity.__dict__) for entity in mdl.entities]
        rslts["transports"] = [Transport.parse_obj(transport.__dict__) for transport in mdl.transports]
        rslts["transportationrequests"] = [TransportationRequest.parse_obj(tr.__dict__) for tr in mdl.transportation_requests.values()]
        rslts["sink"] = Sink.parse_obj(mdl.sink.__dict__)

        return rslts

    # ··················································································································

    # extract results from model (result is in logs)
    results = extract_results(mdl=model)
    # dump model to pickle file
    with pickle_file.open("wb") as f:
        pickle.dump(results,f)

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# MAIN
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def run(data):

    # load data from pickle file
    # data = load_data(scenario_pickle_file)
    # create simulation model
    model = Model(data)
    # run simulation
    model.run()
    # pickle results
    # dump_results(model=model,pickle_file=simulation_pickle_file)
