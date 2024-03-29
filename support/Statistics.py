from support.Event import Event
from support.AccumSum import AccumSum

from configurations.Config import config


class Statistics:

    def __init__(self, numEvents):
        self.lastArrivalsTime = [0, 0]
        self.events = [Event() for i in range(numEvents)]
        self.numbers = [0, 0]        # [ numberB, numberP ]: jobs in the node
        self.number = 0              # total number of B and P requests
        self.processedJobs = [0, 0]        # [ indexB, indexP ]: processed jobs
        self.areas = [0, 0]         # time integrated number in the node */
        self.sum = [AccumSum() for i in range(0, numEvents)] # one for each event

        # init events and sums
        for s in range(0, numEvents - 1):   # excluding sampling events
            self.events[s].t = config.START_B      # this value is arbitrary because all servers are initially idle
            self.events[s].x = 0
        

    def __str__(self) -> str:
        my_str = ''
        for attr, value in vars(self).items():
            if type(value) == list:
                for i in range(len(value)):
                    my_str += f'{attr}[{i}] = {value[i]}\n'
                my_str += '\n'
            else:
                my_str += f'{attr} = {value}\n'
        return my_str
    

    def setSamplingTime(self, samplingTime):
        self.events[len(self.events) - 1].t = samplingTime
        self.events[len(self.events) - 1].x = 1

    def updateArrivalB(self, base_time:float, interarrival:float):
        newTime = base_time + interarrival
        if (newTime > config.FIRST_HALFDAY_CLOSE_TIME) and (newTime < config.SECOND_HALFDAY_OPEN_TIME):
            # in this case, next arrival is at bar reopening. P arrivals is closed and 
            # it will continue with departure until requests are pending
            newTime = config.SECOND_HALFDAY_OPEN_TIME + interarrival
    
        self.events[0].t = newTime
        self.events[0].x = 1
        # close the B-door at the end of day
        if self.events[0].t > config.STOP_B and not (config.FIND_B_VALUE or config.INFINITE_H):
            self.events[0].x = 0


    def updateArrivalP(self, time):
        pArrivalIndex = config.SERVERS_B + 1
        self.events[pArrivalIndex].t = time
        self.events[pArrivalIndex].x = 1

        # close the door if time is over
        if self.events[pArrivalIndex].t > config.STOP_P and \
            not (config.FIND_B_VALUE or config.INFINITE_H): 
            self.events[pArrivalIndex].x = 0

    def newDay(self, newDayFirstArrivals:list):
        # re-acrive sampling event
        self.events[len(self.events) - 1].x = 1
        # re-active b-arrivals
        self.events[0].t = newDayFirstArrivals[0]
        self.events[0].x = 1 
        # re-active p-arrivals
        pArrivalIndex = config.SERVERS_B + 1
        self.events[pArrivalIndex].t = newDayFirstArrivals[1]
        self.events[pArrivalIndex].x = 1 

    def printEvents(self):
        for ev in self.events:
            print(ev)

    
    def resetStats(self):
        # dont reset the number of job in the node to continue from the current state
        numEvents = len(self.events)
        self.processedJobs = [0, 0]        # [ indexB, indexP ]: processed jobs
        self.areas = [0, 0]         # time integrated number in the node */
        self.sum = [AccumSum() for i in range(0, numEvents)] # one for each event
        