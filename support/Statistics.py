from support.Event import Event
from support.AccumSum import AccumSum
from support.Config import START_B, SERVERS_B, STOP_P, STOP_B, SLOTSTIME, FIRST_HALFDAY_CLOSE_TIME, SECOND_HALFDAY_OPEN_TIME

class Statistics:
    # The following variables are meant to store the last arrival of each time
    # in the last day: in fact, it needs to compute the last arrival time for
    # statistical analisys. the compution will be done in the following way:
    #   for B type: t.day * 19 * 60 + ( t.lastBTypeArrival - config.START_B )
    # in the simulated system, everything happens during the 19 hour between
    # 7:00 and 2:00.
    # [ lastBTyypeArrival, lastPTypeArrival ]
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
            self.events[s].t = START_B      # this value is arbitrary because all servers are initially idle
            self.events[s].x = 0              
            self.sum[s].service = 0.0
            self.sum[s].served = 0
        
        # schedule the first p-arrival:


    def setSamplingTime(self, samplingTime):
        self.events[len(self.events) - 1].t = samplingTime
        self.events[len(self.events) - 1].x = 1

    def updateArrivalB(self, base_time:float, interarrival:float):
        # !!!!!!!!!!!!!!!!!!!!
        newTime = base_time + interarrival
        if (newTime > FIRST_HALFDAY_CLOSE_TIME) and (newTime < SECOND_HALFDAY_OPEN_TIME):
            # in this case, next arrival is at bar reopening. P arrivals is closed and 
            # it will continue with departure until requests are pending
            newTime = SECOND_HALFDAY_OPEN_TIME + interarrival
    
        self.events[0].t = newTime
        self.events[0].x = 1
        # close the B-door at the end of day
        if (self.events[0].t > STOP_B):
            self.events[0].x = 0


    def updateArrivalP(self, time):
        pArrivalIndex = SERVERS_B + 1
        self.events[pArrivalIndex].t = time
        self.events[pArrivalIndex].x = 1

        # close the door if time is over
        if (self.events[pArrivalIndex].t > STOP_P): 
            self.events[pArrivalIndex].x = 0

    def newDay(self, newDayFirstArrivals:list):
        # re-acrive sampling event
        self.events[len(self.events) - 1].x = 1
        # re-active b-arrivals
        self.events[0].t = newDayFirstArrivals[0]
        self.events[0].x = 1 
        # re-active p-arrivals
        pArrivalIndex = SERVERS_B + 1
        self.events[pArrivalIndex].t = newDayFirstArrivals[1]
        self.events[pArrivalIndex].x = 1 

    def printEvents(self):
        for ev in self.events:
            print(ev)