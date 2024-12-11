class Simulation:
    def __init__(self, data):
        self.data = data
        self.current_frame = 0

    def update(self):
        if not self.is_finished():
            self.current_frame += 1

    def get_current_data(self):
        return self.data[self.current_frame]

    def is_finished(self):
        return self.current_frame >= len(self.data) - 1

    def get_max_altitude(self):
        return max(d['Smoothed altitude [km]'] for d in self.data)

    def get_max_downrange(self):
        return max(d['Downrange distance [km]'] for d in self.data)