# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# IMPORT
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# 3rd party
import re

# own
from simulation.entities import Entity

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# SETUP
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# CLASSES
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

class Elevator:

    # EVENTS
    START = "START"
    END = "END"
    # ACTIONS
    MOVING = "MOVING"
    OPEN_DOORS = "OPEN DOORS"
    CLOSE_DOORS = "CLOSE DOORS"
    LOAD = "LOAD"
    UNLOAD = "UNLOAD"

    # ··················································································································

    def __init__(self, model, transport_data):

        # from transport_data
        self.model = model
        self.id = transport_data.id
        self.description = transport_data.description
        self.name = transport_data.name
        self.type = transport_data.type
        self.from_datetime = transport_data.from_datetime
        self.from_s = transport_data.from_s
        self.until_datetime = transport_data.until_datetime
        self.until_s = transport_data.until_s
        self.allowed_to_transport = transport_data.allowed_to_transport
        self.on_board = transport_data.on_board
        self.capacity = transport_data.capacity
        self.speed = transport_data.speed
        self.fixload_time = transport_data.fixload_time
        self.varload_time = transport_data.varload_time
        self.fixunload_time = transport_data.fixunload_time
        self.varunload_time = transport_data.varunload_time
        self.strategy = transport_data.strategy
        self.connections = transport_data.connections
        self.queues = transport_data.queues
        self.idle = transport_data.idle
        self.log = transport_data.log
        # additional attributes
        self.current_wa = self.idle
        self.next_wa = self.idle
        self.next_stop = self.idle
        self.list_of_requests = list()
        self.waiting_wa = list()
        self.moving_direction = 1
        self.strategies = {"stupid": self.__set_next_stop_stupid,
                           "ok": self.__set_next_stop_ok}

    # ··················································································································

    def __set_next_stop(self):
        """
        Method that choses the set next whereabout method in a strategy pattern.
        """

        return self.strategies[self.strategy]()

    # ··················································································································

    def __set_next_stop_stupid(self):
        """
        Method that sets the next whereabout in a stupid fashion. It is just the next whereabout. The next stop defines
        whether entiteis are allowed to leave/enter there or not.
        """

        # TODO: Zentral auf Lift definieren und nicht immer neu berechnen...
        all_was = list(self.connections.keys())
        wa_floor_lookup = {wa: [int(floor) for floor in re.findall(r"\d+",wa)][0] for wa in all_was}
        min_floor = min(wa_floor_lookup.values())
        min_wa = list(filter(lambda x: wa_floor_lookup[x] == min_floor,wa_floor_lookup))[0]
        max_floor = max(wa_floor_lookup.values())
        max_wa = list(filter(lambda x: wa_floor_lookup[x] == max_floor,wa_floor_lookup))[0]

        current_floor = wa_floor_lookup[self.current_wa]
        possible_next_was = self.connections[self.current_wa]
        possible_next_floors = [wa_floor_lookup[possible_next_wa] for possible_next_wa in possible_next_was]

        # moving down
        if self.current_wa == max_wa:
            self.moving_direction = -1
        # moving up
        if self.current_wa == min_wa:
            self.moving_direction = 1

        next_floor = current_floor + self.moving_direction
        self.next_stop = list(filter(lambda x: wa_floor_lookup[x] == next_floor, wa_floor_lookup))[0]

    # ··················································································································

    def __set_next_stop_ok(self):
        """
        Method that sets the next whereabout in a 'ok' fashion. It is just the next whereabout. The next stop defines
        whether entiteis are allowed to leave/enter there or not.
        """

        # TODO: Zentral auf Lift definieren und nicht immer neu berechnen...
        all_was = list(self.connections.keys())
        wa_floor_lookup = {wa: [int(floor) for floor in re.findall(r"\d+",wa)][0] for wa in all_was}
        min_floor = min(wa_floor_lookup.values())
        min_wa = list(filter(lambda x: wa_floor_lookup[x] == min_floor,wa_floor_lookup))[0]
        max_floor = max(wa_floor_lookup.values())
        max_wa = list(filter(lambda x: wa_floor_lookup[x] == max_floor,wa_floor_lookup))[0]

        current_floor = wa_floor_lookup[self.current_wa]
        possible_next_was = self.connections[self.current_wa]
        possible_next_floors = [wa_floor_lookup[possible_next_wa] for possible_next_wa in possible_next_was]

        # was_where_people_need_to_leave_transport
        tr_of_entities_in_transport = [entity.active_tr for entity in self.on_board]
        goal_was_of_trs = list(set([self.model.transportation_requests[tr].end_wa for tr in tr_of_entities_in_transport]))
        goal_floors_of_trs = [wa_floor_lookup[goal_wa] for goal_wa in goal_was_of_trs]

        was_where_people_are_waiting = [wa.name for wa in self.model.whereabouts.values() if any(len(wa.queues[q]) != 0 for q in self.queues)]
        floors_where_people_are_waiting = [wa_floor_lookup[waiting_wa] for waiting_wa in was_where_people_are_waiting]

        # Decision for next wa
        # if no entity in transport and no entity waiting -> just stay where it is
        if len(goal_floors_of_trs) == 0 and len(floors_where_people_are_waiting) == 0:
            next_floor = current_floor
        # if no entity in transport but entities are waitng -> go to closest wa where entities are waiting
        elif len(goal_floors_of_trs) == 0 and len(floors_where_people_are_waiting) > 0:
            next_floor = min(floors_where_people_are_waiting, key=lambda x: (abs(x - current_floor), x))

        # if entity in transport -> go to closest wa where entities are leaving
        elif len(goal_floors_of_trs) > 0:
            next_floor = min(goal_floors_of_trs, key=lambda x: (abs(x - current_floor), x))

        self.next_stop = list(filter(lambda x: wa_floor_lookup[x] == next_floor, wa_floor_lookup))[0]

        # # moving down
        # if self.current_wa == max_wa:
        #     self.moving_direction = -1
        # # moving up
        # if self.current_wa == min_wa:
        #     self.moving_direction = 1
        #
        # next_floor = current_floor + self.moving_direction
        # self.next_wa = list(filter(lambda x: wa_floor_lookup[x] == next_floor, wa_floor_lookup))[0]

    # ··················································································································

    def __set_next_whereabout(self):
        """
        Method that sets the next stop. Stop means, where the transport STOPS and let people exit and enter.
        """

        all_was = list(self.connections.keys())
        wa_floor_lookup = {wa: [int(floor) for floor in re.findall(r"\d+",wa)][0] for wa in all_was}
        min_floor = min(wa_floor_lookup.values())
        min_wa = list(filter(lambda x: wa_floor_lookup[x] == min_floor,wa_floor_lookup))[0]
        max_floor = max(wa_floor_lookup.values())
        max_wa = list(filter(lambda x: wa_floor_lookup[x] == max_floor,wa_floor_lookup))[0]

        current_floor = wa_floor_lookup[self.current_wa]
        possible_next_was = self.connections[self.current_wa]
        possible_next_floors = [wa_floor_lookup[possible_next_wa] for possible_next_wa in possible_next_was]

        next_stop_floor = wa_floor_lookup[self.next_stop]
        if next_stop_floor > current_floor:
            next_wa_floor = current_floor + 1
        elif next_stop_floor < current_floor:
            next_wa_floor = current_floor - 1
        else:
            next_wa_floor = current_floor

        self.next_wa = list(filter(lambda x: wa_floor_lookup[x] == next_wa_floor,wa_floor_lookup))[0]

    # ··················································································································

    def __calc_traveltime(self):
        """
        Method that calculates the traveltime.
        """

        distance = self.model.dima[self.current_wa][self.next_wa]
        traveltime = distance / self.speed

        if traveltime == 0:
            traveltime = 1

        return traveltime

    # ··················································································································

    def __remove_entities_from_transport(self):
        """
        Method that removes the entities from the transportation device.
        """

        # initialize timeout
        timeout = 0
        # get transportation-requests from entities in transport
        # TODO: Is this next line really needed?
        transportation_request = [self.model.transportation_requests[entity.active_tr] for entity in self.on_board]
        # get entities that are staying in transport and those that are leaving the transport
        entities_staying = [entity for entity in self.on_board if self.model.transportation_requests[entity.active_tr].end_wa != self.current_wa]
        entities_leaving = [entity for entity in self.on_board if self.model.transportation_requests[entity.active_tr].end_wa == self.current_wa]

        # if entities are to be unload...
        if len(entities_leaving) != 0:
            # set the entities that are staying in transport
            self.on_board = entities_staying
            # process leaving entities...
            for entity in entities_leaving:
                # update whereabout
                entity.current_wa = self.current_wa
                # Time to unload passenger
                timeout += self.varunload_time
                # ······································································································
                # LOG
                entity.add_log_entry(time=self.model.env.now + timeout,
                                     event=Entity.END,
                                     action=Entity.TRANSPORT,
                                     whereabout=entity.current_wa)
                entity.print_latest_log_entry()
                # ······································································································
                # put entity in queue
                self.model.logic.put_in_queue(entity,timeout)

        return timeout

    # ··················································································································

    def __put_entities_in_transport(self):
        """
        Method that puts entities in the transportation device.
        """

        # initialize timeout
        timeout = 0
        # Initialize counter for passengers that are entering on that floor
        num_entities_entering = 0
        # get number of queueing passengers on that floor
        num_queueing_entities = sum([len(self.model.whereabouts[self.current_wa].queues[queue]) for queue in self.queues])

        # add queueing entities to transport until capacity is reached
        while len(self.on_board) < self.capacity and num_queueing_entities > 0:
            # choose longest queue to get passenger from
            queue_lengths = [len(self.model.whereabouts[self.current_wa].queues[queue]) for queue in self.queues]
            idx_of_longest_queue = queue_lengths.index(max(queue_lengths))
            name_of_longest_queue = self.queues[idx_of_longest_queue]
            # remove entity from queue and add to transport
            entity = self.model.whereabouts[self.current_wa].queues[name_of_longest_queue].pop(0)
            self.on_board.append(entity)
            # time to load
            timeout += self.varload_time
            # ··········································································································
            # LOG
            # Log the end of waiting on entity
            entity.add_log_entry(time=self.model.env.now + timeout,
                                 event=Entity.END,
                                 action=Entity.WAITING,
                                 whereabout=self.current_wa)
            entity.print_latest_log_entry()
            # Log the start of transport on entity
            entity.add_log_entry(time=self.model.env.now+timeout,
                                 event=Entity.START,
                                 action=Entity.TRANSPORT,
                                 whereabout=self.current_wa)
            entity.print_latest_log_entry()
            # Log the change in the whereabout
            self.model.whereabouts[self.current_wa].add_log_entry(time=self.model.env.now + timeout,
                                                                  queue=name_of_longest_queue,
                                                                  amount=-1)
            self.model.whereabouts[self.current_wa].print_latest_log_entry()
            # ··········································································································
            # increase counter and update queueing passengers
            num_entities_entering += 1
            # update the number of entities waiting at that whereabout
            num_queueing_entities = sum([len(self.model.whereabouts[self.current_wa].queues[queue]) for queue in self.queues])

        return timeout

    # ··················································································································

    def add_log_entry(self, time, event, action, whereabout):

        log_entry = {"time": time, "event": event, "action": action, "whereabout": whereabout}
        self.log.append(log_entry)

    # ··················································································································

    def print_latest_log_entry(self):

        log_entry = self.log[-1]
        print(f"{log_entry['time']:7.2f}: Transport {self.name} : {log_entry['event']} : {log_entry['action']} : {log_entry['whereabout']}")

    # ··················································································································

    def transport_entities(self):
        """
        Method that transports the entities with the transport.
        """

        while True:

            if self.current_wa == self.next_stop:
                # ··········································································································
                # LOG ARRIVAL
                self.add_log_entry(time=self.model.env.now,
                                   event=Elevator.END,
                                   action=Elevator.MOVING,
                                   whereabout=self.current_wa)
                self.print_latest_log_entry()
                # ··········································································································
                # get id of transportation-requests from entities in elevator
                transportation_request_ids = [entity.active_tr for entity in self.on_board]
                # get transportation_requests by id
                transportation_requests = [self.model.transportation_requests[tr_id] for tr_id in transportation_request_ids]
                # check end_wa of transportation-requests
                num_entities_to_unload = len([tr.entity_name for tr in transportation_requests if tr.end_wa == self.current_wa])
                num_entities_to_load = sum([len(self.model.whereabouts[self.current_wa].queues[queue]) for queue in self.queues])

                # any entities to load or unload?
                if num_entities_to_unload > 0 or num_entities_to_load > 0:
                    # ······································································································
                    # LOG START OPENING DOOR
                    self.add_log_entry(time=self.model.env.now,
                                       event=Elevator.START,
                                       action=Elevator.OPEN_DOORS,
                                       whereabout=self.current_wa)
                    self.print_latest_log_entry()
                    # ······································································································
                    # open door
                    # TODO: Naming of fixunload not so good... opening also needed when only loading, duh!
                    yield self.model.env.timeout(self.fixunload_time)
                    # ······································································································
                    # LOG END OPENING DOOR
                    self.add_log_entry(time=self.model.env.now,
                                       event=Elevator.END,
                                       action=Elevator.OPEN_DOORS,
                                       whereabout=self.current_wa)
                    self.print_latest_log_entry()
                    # ······································································································

                # unload entities
                if num_entities_to_unload > 0:
                    # ······································································································
                    # LOG START UNLOADING ENTITIES
                    self.add_log_entry(time=self.model.env.now,
                                       event=Elevator.START,
                                       action=Elevator.UNLOAD,
                                       whereabout=self.current_wa)
                    self.print_latest_log_entry()
                    # ······································································································
                    # unload entities
                    timeout = self.__remove_entities_from_transport()
                    yield self.model.env.timeout(timeout)
                    # ······································································································
                    self.add_log_entry(time=self.model.env.now,
                                       event=self.END,
                                       action=self.UNLOAD,
                                       whereabout=self.current_wa)
                    self.print_latest_log_entry()
                    # ······································································································

                # load entities
                if num_entities_to_load > 0:
                    # ······································································································
                    # LOG START LOADING ENTITIES
                    self.add_log_entry(time=self.model.env.now,
                                       event=Elevator.START,
                                       action=Elevator.LOAD,
                                       whereabout=self.current_wa)
                    self.print_latest_log_entry()
                    # ······································································································
                    # load entities
                    timeout = self.__put_entities_in_transport()
                    yield self.model.env.timeout(timeout)
                    # ······································································································
                    # LOG END LOADING ENTITIES
                    self.add_log_entry(time=self.model.env.now,
                                       event=Elevator.END,
                                       action=Elevator.LOAD,
                                       whereabout=self.current_wa)
                    self.print_latest_log_entry()
                    # ······································································································

                # any entities to load or unload?
                if num_entities_to_unload > 0 or num_entities_to_load > 0:
                    # ······································································································
                    # LOG START CLOSING DOORS
                    self.add_log_entry(time=self.model.env.now,
                                       event=Elevator.START,
                                       action=Elevator.CLOSE_DOORS,
                                       whereabout=self.current_wa)
                    self.print_latest_log_entry()
                    # ······································································································
                    # close doors
                    yield self.model.env.timeout(self.fixload_time)
                    # ······································································································
                    # LOG END CLOSING DOORS
                    self.add_log_entry(time=self.model.env.now,
                                       event=Elevator.END,
                                       action=Elevator.CLOSE_DOORS,
                                       whereabout=self.current_wa)
                    self.print_latest_log_entry()
                    # ······································································································
                # ······································································································
                # LOG DEPARTURE
                self.add_log_entry(time=self.model.env.now,
                                   event=Elevator.START,
                                   action=Elevator.MOVING,
                                   whereabout=self.current_wa)
                self.print_latest_log_entry()
                # ······································································································

                # set next stop
                self.__set_next_stop()

            # set next stop where vehicle lets entities leave and hop on
            self.__set_next_whereabout()

            # depart and move to next whereabout
            yield self.model.env.timeout(self.__calc_traveltime())
            self.current_wa = self.next_wa

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
