from support.SamplingEvent import SamplingEvent
import support.Config as config

class SamplingList:

    # list of objects SamplingEvent
    sampleList = None
    numSample = 0
    averageAreas = 0
    averageServices = None
    averageServedPerDay = None
    averageProcessedPerDay = None
    averageInterarrivals = None

    # this is sample caught when 365th day is over to trace global stats with balance
    endSimulationSample = None

    def __init__(self):
        self.sampleList = []
        # adding the service relative to the first event (B-arrival): 
        # i want to keep the same event list indexes for this list
        self.averageServices = [0]
        self.averageServedPerDay = [0]

        self.averageIndexes = []

    
    def append(self, newEvent:SamplingEvent):
        self.sampleList.append(newEvent)
        self.numSample += 1

    def setEndSimSample(self, sample:SamplingEvent):
        self.endSimulationSample = sample

    def computeAverageArea(self):
        tmpB = 0
        tmpP = 0
        for sample in self.sampleList:
            tmpB += sample.areas[0]
            tmpP += sample.areas[1]
        self.averageAreas = [tmpB / self.numSample, tmpP / self.numSample]
    

    def computeServicesMeans(self):

        pArrivalIndex = config.SERVERS_B + 1
        for s in range(1, len(self.endSimulationSample.sum) - 1): 
            
            if s == pArrivalIndex: #the arrivalP event, then skip
                self.averageServices.append(0)
                continue
            
            servedTot = self.endSimulationSample.sum[s].served
            serviceTot = self.endSimulationSample.sum[s].service

            service = serviceTot / servedTot    
            
            self.averageServices.append(service)
            self.averageServedPerDay.append(servedTot / config.STOP )
      

    def computeMeanIndexes(self):
        indexes = [0, 0] 
        for sample in self.sampleList:
            indexes[0] += sample.indexes[0] 
            indexes[1] += sample.indexes[1]
        self.indexes = [int(i / self.numSample) for i in indexes]
    

    def computeMeanInterarrivals(self):
        self.averageInterarrivals = []
        # working_h hours/day * 60 min/hours * config.stop day = total time in minutes 
        totalTimeB = config.B_WORKING_HOURS * 60 * config.STOP
        totalTimeP = config.P_WORKING_HOURS * 60 * config.STOP



    def evaluation(self):
        titles = ["BAR:\n", "PIZZERIA:\n"]
        indexes = None
        stop = config.STOP

        if self.numSample == 1:
            # STEADY ANALISYS
            indexes = self.sampleList[0].indexes 
            index = indexes[0] + indexes[1]
            print("\nfor {0:1d} jobs the service node statistics are:\n".format(index))
            
        else:
            # TRANSIENT ANALISYS
            print("\n\nTransient analisys:")

            # computing means
            #
            # computing average index 
            
            self.computeMeanIndexes()
            index = sum(self.indexes)
            print("\nfor {0:1d} jobs the service node statistics are:\n".format(index))

            # computing average interarrivals
            #self.()

            # computing average areas
            self.computeAverageArea()

            # computing mean served and service time for each server:
            self.computeServicesMeans()
