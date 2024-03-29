import copy

from configurations.Config import config

class Time:
    current = None          # current time in minutes            */
    next = None             # next (most imminent) event time in minutes  */
    dayOfWeek = None        # used to trace week or weekend interarrivals

    timeSlot = None         # current slot indicator
    changeBatchTimeB = None
    changeBatchTimeP = None
    simulationTimeB = None # effectively simulated time
    simulationTimeP = None # effectively simulated time

    def __init__(self):
        self.current = config.START_B
        self.dayOfWeek = config.SIMULATE_WEEK # starting from the first working day
        self.timeSlot = 0
        self.changeBatchTimeB = config.START_B
        self.changeBatchTimeP = config.START_P
        self.simulationTimeB = 0
        self.simulationTimeP = 0

    def __str__(self) -> str:
        my_str = ''
        for attr, value in vars(self).items():
            my_str += f'{attr} = {value}\n'
        return my_str

    def changeSlot(self):
    #   note that t.current cannot be lower than the first element of the
    #   c.SLOTSTIME: t.current is initialized at c.START_B every 'new day starts',
    #   and c.START_B is the first element of c.SLOTSTIME.

        if not (config.FIND_B_VALUE or config.INFINITE_H):
            newSlot = 0
            for i in range(1, len(config.SLOTSTIME)):
                # finding the biggest possible slotsTime that is lower than current.
                # if time is equal to slotTime[i], the arrival rate is changed yet.
                if (config.SLOTSTIME[i] <= self.current):
                    newSlot = i
                else: #others are bigger 
                    break
            # it's possible that newSlot reference the slot in 15 -> 18, but there won't be arrivals:
            # the bar is working on pending requests
            self.timeSlot = newSlot

    def copy(self):
        return copy.deepcopy(self)

    def setBatchTime(self):
        # self.current -= scaleFactor
        # self.next -= scaleFactor
        self.changeBatchTimeB = self.current
        self.changeBatchTimeP = self.current
        self.simulationTimeB = 0
        self.simulationTimeP = 0
