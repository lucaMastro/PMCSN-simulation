class Event:
    t = None  #next event time
    x = None  #event status, 0 or 1

    def __str__(self):
        return f't: {self.t} == {self.t/60} ; x: {self.x}'

    def __str__(self) -> str:
        return f't: {self.t}; x: {self.x}'
        