# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# IMPORT
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# built-in
import random

# own
from simulation.entities import Entity

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# SETUP
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# CLASSES
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

class Logic:

    # ··················································································································

    def __init__(self, model):

        self.model = model
        self.log = list()

    # ··················································································································

    def put_in_queue(self, entity, timeout=0):
        """
        Method decides in which queue to put a given entity.
        """

        # get active transportaiton-request of entity
        transportation_request = self.model.transportation_requests[entity.active_tr]

        # if entitey has reached end-whereabout
        if entity.current_wa == transportation_request.end_wa:

            # what's the entities behavior when end_wa is reached?
            if transportation_request.behavior == "work":
                # put in working queue at current-whereabout
                self.model.whereabouts[entity.current_wa].queues["work"].append(entity)
                # TODO: Maybe interesting to log the queue on entity level too...
                # TODO: move active transportation_request to closed ones
                # TODO: Problably set next active transportation request...
                # ······································································································
                # LOG ARRIVAL AT END-WHEREABOUT
                # LOG ON ENTITY
                entity.add_log_entry(time=self.model.env.now + timeout,
                                     event=Entity.START,
                                     action=Entity.WAITING,
                                     whereabout=entity.current_wa)
                # LOG ON WHEREABOUT
                self.model.whereabouts[entity.current_wa].add_log_entry(time=self.model.env.now + timeout,
                                                                        queue="work",
                                                                        amount=entity.quantity)
                # ······································································································
            elif transportation_request.behavior == "store":
                # put in storing queue at current-whereabout
                self.model.whereabouts[entity.current_wa].queues["store"].append(entity)
                # TODO: Maybe interesting to log the queue on entity level too...
                # TODO: move active transportation_request to closed ones
                # TODO: Problably set next active transportation request...
                # ······································································································
                # LOG ARRIVAL AT END-WHEREABOUT
                # LOG ON ENTITY
                entity.add_log_entry(time=self.model.env.now + timeout,
                                     event=Entity.START,
                                     action=Entity.WAITING,
                                     whereabout=entity.current_wa)
                # LOG ON WHEREABOUT
                self.model.whereabouts[entity.current_wa].add_log_entry(time=self.model.env.now + timeout,
                                                                        queue="store",
                                                                        amount=entity.quantity)
                # ······································································································
            elif transportation_request.behavior == "disappear":
                # put in passing queue at current-whereabout
                self.model.whereabouts[entity.current_wa].queues["pass"].append(entity)
                # TODO: Maybe interesting to log the queue on entity level too...
                # ······································································································
                # LOG ARRIVAL AT END-WHEREABOUT
                # LOG ON ENTITY
                entity.add_log_entry(time=self.model.env.now + timeout,
                                     event=Entity.START,
                                     action=Entity.WAITING,
                                     whereabout=entity.current_wa)
                # LOG ON WHEREABOUT
                self.model.whereabouts[entity.current_wa].add_log_entry(time=self.model.env.now + timeout,
                                                                        queue="pass",
                                                                        amount=entity.quantity)
                # ······································································································
                # remove from passing-queue
                self.model.whereabouts[entity.current_wa].queues["pass"].remove(entity)
                # ······································································································
                # LOG ON WHEREABOUT
                # LOG ON ENTITY
                entity.add_log_entry(time=self.model.env.now + timeout,
                                     event=Entity.END,
                                     action=Entity.WAITING,
                                     whereabout=entity.current_wa)
                self.model.whereabouts[entity.current_wa].add_log_entry(time=self.model.env.now + timeout,
                                                                        queue="pass",
                                                                        amount=-entity.quantity)
                # ······································································································
                # put entity in sink
                entity.current_wa = self.model.sink.name
                self.model.sink.entities.append(entity)
                # ······································································································
                # LOG ARRIVAL AT SINK
                # LOG ON ENTITY
                entity.add_log_entry(time=self.model.env.now + timeout,
                                     event=Entity.END,
                                     action=Entity.LIFE,
                                     whereabout=entity.current_wa)
                # LOG ON SINK
                self.model.sink.add_log_entry(time=self.model.env.now + timeout,
                                              queue="sink",
                                              amount=entity.quantity)
                # ······································································································
            else:
                raise NotImplementedError("No other behaviors defined...")

        # if entity has not reached end-whereabout
        else:
            # if entity was just created (initialized with None)
            if entity.current_wa is None:
                # update entity whereabout to start-whereabout
                entity.current_wa = transportation_request.start_wa
            # put entity in queue
            # TODO: Better select in which queue to put an entity... (Now always in E0-queue)
            # TODO: HERE IS WHERE THE MAGIC WILL HAPPEN....
            # Random selection
            choices = ["E0"]
            selected_queue = random.choice(choices)
            self.model.whereabouts[entity.current_wa].queues[selected_queue].append(entity)

            # Always in the same predefinded queue
            # self.model.whereabouts[entity.current_wa].queues["E0"].append(entity)
            # ··········································································································
            # LOG ARRIVAL AT END-WHEREABOUT
            # LOG ON ENTITY
            entity.add_log_entry(time=self.model.env.now + timeout,
                                 event=Entity.START,
                                 action=Entity.WAITING,
                                 whereabout=entity.current_wa)
            # LOG ON WHEREABOUT
            self.model.whereabouts[entity.current_wa].add_log_entry(time=self.model.env.now + timeout,
                                                                    queue=selected_queue,
                                                                    amount=entity.quantity)
            # ··········································································································
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
