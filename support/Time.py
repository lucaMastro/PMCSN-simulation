import copy
import support.Config as c

class Time:
    current = None          # current time in minutes            */
    next = None             # next (most imminent) event time in minutes  */
    day = None              # used to trace all days simulated. The end of
                            # simulation is computed on this value

    dayOfWeek = None        # used to trace week or weekend interarrivals
    # monday = 0            
    # tuesday = 1
    # wednesday = 2
    # thursday = 3
    # friday = 4
    # saturday = 5
    # sunday = 6

    timeSlot = None         # current slot indicator
    
    def __init__(self):
        self.current = c.START_B         
        self.day = 0 
        self.dayOfWeek = 0 # starting from the first working day
        self.timeSlot = 0
        self.notWorkingDays = 0

    def changeSlot(self):
    #   note that t.current cannot be lower than the first element of the
    #   c.SLOTSTIME: t.current is initialized at c.START_B every 'new day starts',
    #   and c.START_B is the first element of c.SLOTSTIME.
        newSlot = 0
        for i in range(1, len(c.SLOTSTIME)):
            # finding the biggest possible slotsTime that is lower than current.
            # if time is equal to slotTime[i], the arrival rate is changed yet.
            if (c.SLOTSTIME[i] <= self.current):
                newSlot = i
            else: #others are bigger 
                break
        # it's possible that newSlot reference the slot in 15 -> 18, but there won't be arrivals:
        # the bar is working on pending requests
        self.timeSlot = newSlot

    def copy(self):
        return copy.deepcopy(self)

    def newDay(self):
        self.current = c.START_B
        self.day += 1
        self.dayOfWeek = (self.dayOfWeek + 1) % 7