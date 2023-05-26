# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# IMPORT
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# own
from simulation.entities import Entity

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# SETUP
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# CLASSES
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

class Source:

    # ··················································································································

    def __init__(self, env, model, transportation_requests, entities):

        self.env = env
        self.model = model
        self.transportation_requests = transportation_requests
        self.data_entities = entities

    # ··················································································································

    def create_entities(self):
        """
        Method loops through all transportation-requests and initiates the required action (generate entity, pull from storage, ...)
        """

        for transportation_request in self.transportation_requests:

            # get entity_name from transportation_request
            entity_name = transportation_request.entity_name
            # get all entity_data
            data_entity = [data_ent for data_ent in self.data_entities if data_ent.name == entity_name][0]
            # calculate time until this transportation-request is supposed to start
            time_to_arrival = transportation_request.start_s - self.env.now

            # wait, if necessary
            if time_to_arrival != 0:
                yield self.env.timeout(time_to_arrival)

            # create entity
            entity = Entity(data_entity=data_entity)

            # TODO: Later, when multiple TR per entity - Check if entity exists and then remove from store/working queue...

            # remove current transportation_request from open_tr
            entity.open_tr.remove(transportation_request.id)
            # put current transportation_request in active_tr
            entity.active_tr = transportation_request.id

            # append entity in entities-list
            self.model.entities.append(entity)

            # ··········································································································
            # LOG
            entity.add_log_entry(time=self.env.now,
                                 event=Entity.START,
                                 action=Entity.LIFE,
                                 whereabout=transportation_request.start_wa)
            entity.print_latest_log_entry()
            # ··········································································································

            self.model.logic.put_in_queue(entity)

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
