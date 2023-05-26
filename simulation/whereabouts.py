# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# IMPORT
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# SETUP
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# CLASSES
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

class Whereabout:

    # ··················································································································

    def __init__(self, env, whereabout_data):

        self.env = env
        self.id = whereabout_data.id
        self.description = whereabout_data.description
        self.name = whereabout_data.name
        self.capacity = whereabout_data.capacity
        self.queues = {queue: list() for queue in whereabout_data.queues}
        self.from_datetime = whereabout_data.from_datetime
        self.from_s = whereabout_data.from_s
        self.until_datetime = whereabout_data.until_datetime
        self.until_s = whereabout_data.until_s
        self.log = whereabout_data.log

    # ··················································································································

    def add_log_entry(self, time, queue, amount):
        log_entry = {"time": time, "queue": queue, "amount": amount}
        self.log.append(log_entry)

    # ··················································································································

    def print_latest_log_entry(self):

        log_entry = self.log[-1]
        print(f"{log_entry['time']:7.2f}: Whereabout {self.name} : {log_entry['queue']} : {log_entry['amount']}")


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
