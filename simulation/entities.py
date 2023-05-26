# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# IMPORT
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# SETUP
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# CLASSES
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

class Entity:

    # EVENTS
    START = "START"
    END = "END"
    # ACTIONS
    LIFE = "LIFE"
    TRANSPORT = "TRANSPORT"
    WAITING = "WAITING"

    def __init__(self, data_entity):
        self.id = data_entity.id
        self.description = data_entity.description
        self.name = data_entity.name
        self.type = data_entity.type
        self.quantity = data_entity.quantity
        self.current_wa = data_entity.current_wa
        self.current_behavior = data_entity.current_behavior
        self.active_tr = data_entity.active_tr
        self.open_tr = data_entity.open_tr
        self.closed_tr = data_entity.closed_tr
        self.log = data_entity.log

    # ··················································································································

    def add_log_entry(self,time, event, action, whereabout):

        log_entry = {"time": time, "event": event, "action": action, "whereabout": whereabout}
        self.log.append(log_entry)

    # ··················································································································

    def print_latest_log_entry(self):

        log_entry = self.log[-1]
        print(f"{log_entry['time']:7.2f}: Entity {self.name} : {log_entry['event']} : {log_entry['action']} : {log_entry['whereabout']}")

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
