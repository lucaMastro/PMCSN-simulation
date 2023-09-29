from support.SamplingEvent import SamplingEvent
from math import sqrt
from configurations.Config import config
from support.rvms import idfStudent
from copy import deepcopy

def makeDict():
    d = dict()
    d['mean'] = 0
    d['variance'] = 0
    d['autocorrelation'] = 0
    d['confidence_interval_length'] = 0
    d['stdev'] = 0
    return d

def computeAutocorrelation(l: list, mean:float, variance: float):
    n = len(l)
    cj = 0
    for i in range(n - 1):
        cj += (l[i] - mean) * (l[i+1] - mean)
    cj /= (n - 1)
    return cj/variance


class SamplingList:

    # list of objects SamplingEvent
    sampleListB = None
    sampleListP = None
    numSampleB = 0
    numSampleP = 0

    """ those statistics will keep mean and variance for both cases B and P. they are list of 2 dict:
     ------------------B_DICT-------------,   ------------------P_DICT-------------
    [{'mean' = xi, 'variance' = (xj - xi)^2}, {'mean' = xi, 'variance' = (xj - xi)^2}]
    
    the above statistics are computed with welford one-pass algho """
    avgInterarrivals = None
    avgWaits = None
    avgNumNodes = None
    avgDelays = None
    avgNumQueues = None
    """ server stats are utilization, service, share. It needs mean and variance for each of them.
    it will be a dict of dict; where s is server index.
    {
      s: {
          'utilization': {
              'mean': 0,
              'variance': 0    
          }
          'service': {
              'mean': 0,
              'variance' = 0
          }
          'share': {
              'mean': 0,
              'variance' = 0
          }
      }
    }
    """
    serversStats = None

    """ the autocorrelation of each statistic is not important inside the single batch. Since it is
        used this struct for keep batches but also for computed lag j beetwen batches, it's 'append'
        algho is differentiate by the following boolean:    
    """
    
    processedJobs = None


    def __init__(self):
        #self. computeAutocorrelation = computeAutocorr

        self.sampleListB = []
        self.sampleListP = []

        self.avgInterarrivals = [makeDict(), makeDict()]
        self.avgWaits = [makeDict(), makeDict()]
        self.avgNumNodes = [makeDict(), makeDict()]
        self.avgDelays = [makeDict(), makeDict()]
        self.avgNumQueues = [makeDict(), makeDict()]
        self.processedJobs = [0, 0]
        self.serversStats = dict()
        for s in list(range(1, config.SERVERS_B + 1)) + list(range(config.SERVERS_B + 2, config.SERVERS_B + 2 + config.SERVERS_P)):
    
            self.serversStats[s] = dict()
            self.serversStats[s]['utilization'] = dict()
            self.serversStats[s]['service'] = dict()
            self.serversStats[s]['share'] = dict()

            self.serversStats[s]['utilization']['mean'] = 0
            self.serversStats[s]['utilization']['variance'] = 0
            self.serversStats[s]['utilization']['autocorrelation'] = 0
            self.serversStats[s]['utilization']['confidence_interval_length'] = 0
            self.serversStats[s]['utilization']['stdev'] = 0

            self.serversStats[s]['service']['mean'] = 0
            self.serversStats[s]['service']['variance'] = 0
            self.serversStats[s]['service']['autocorrelation'] = 0
            self.serversStats[s]['service']['confidence_interval_length'] = 0
            self.serversStats[s]['service']['stdev'] = 0

            self.serversStats[s]['share']['mean'] = 0
            self.serversStats[s]['share']['variance'] = 0
            self.serversStats[s]['share']['autocorrelation'] = 0
            self.serversStats[s]['share']['confidence_interval_length'] = 0
            self.serversStats[s]['share']['stdev'] = 0


    def __str__(self) -> str:
        titles = ["Bar", "Pizzeria"]
        sizes = [self.numSampleB, self.numSampleP]
        my_string = "Sample List statistics are:\n"
        for i in range(2):
            my_string += f'for {self.processedJobs[i]} jobs in the {titles[i]} and {sizes[i]} sample:\n'
            my_string += "        statistic          mean    variance      conf int\n"
            my_string += "  avg interarrivals .. : {0:6.3f}    {1:6.3f}        {2:6.3f}\n".\
                format(self.avgInterarrivals[i]['mean'],
                    self.avgInterarrivals[i]['variance'],
                    self.avgInterarrivals[i]['confidence_interval_length'])

            my_string += "  avg wait ........... : {0:6.3f}    {1:6.3f}        {2:6.3f}\n".\
                format(self.avgWaits[i]['mean'],
                    self.avgWaits[i]['variance'],
                    self.avgWaits[i]['confidence_interval_length'])
            
            my_string += "  avg # in node ...... : {0:6.3f}    {1:6.3f}        {2:6.3f}\n".\
                format(self.avgNumNodes[i]['mean'],
                    self.avgNumNodes[i]['variance'],
                    self.avgNumNodes[i]['confidence_interval_length'])
            
            my_string += "  avg delay .......... : {0:6.3f}    {1:6.3f}        {2:6.3f}\n".\
                format(self.avgDelays[i]['mean'], 
                    self.avgDelays[i]['variance'], 
                    self.avgDelays[i]['confidence_interval_length'])
            
            my_string += "  avg # in queue ..... : {0:6.3f}    {1:6.3f}        {2:6.3f}\n".\
                format(self.avgNumQueues[i]['mean'],
                    self.avgNumQueues[i]['variance'],
                    self.avgNumQueues[i]['confidence_interval_length'])
            
            my_string += "\nthe server statistics are:\n"
            my_string += "    server     utilization     avg service +/- w        share\n"
            startingPoint = None
            endingPoint = None
            if (i == 0):
                startingPoint = 1
                endingPoint = config.SERVERS_B + 1
            else:
                startingPoint = config.SERVERS_B + 2 
                endingPoint = config.SERVERS_B + 2 + config.SERVERS_P
            for s in range(startingPoint, endingPoint):  
                my_string += "{0:8d} {1:14.3f} {2:15.3f} +/- {3:.3f} {4:15.3f}\n".\
                    format(s, self.serversStats[s]['utilization']['mean'], 
                        self.serversStats[s]['service']['mean'], 
                        self.serversStats[s]['service']['confidence_interval_length'], 
                        self.serversStats[s]['share']['mean'])
            my_string += '\n\n'
        return my_string
    

    def newLine(self, kind:int, addLegend:bool = None) -> str:
        # kind == 0: B-type; kind == 1: P-type
        string = ''
        num = self.numSampleB if kind == 0 else self.numSampleP

        if addLegend:
            string = 'num. sample,statistic,mean,variance,std dev,w (interval length/2)\n'
        
        for attr, value in vars(self).items():
            if attr in ('sampleListB', 'serversStats', 'sampleListP', \
                'numSampleB', 'numSampleP', 'computeAutocorrelation', 'processedJobs'):
                    continue
            
            m = value[kind]['mean']
            variance = value[kind]['variance']
            std_dev = value[kind]['stdev']
        
            interval = value[kind]['confidence_interval_length']
            
            string += f'{num},{attr},{m:.3f},{variance:.3f},{std_dev:.3f},{interval:.3f}\n'
        
        firstServerIndex = None
        # the following keep lastServerIndex + 1. It's the right extreme of for cycle
        lastServerIndexPlus = None
        if kind == 0:
            firstServerIndex = 1
            lastServerIndexPlus = config.SERVERS_B + 1
        else:
            firstServerIndex = config.SERVERS_B + 2
            lastServerIndexPlus = config.SERVERS_B + 2 + config.SERVERS_P

        for s in range(firstServerIndex, lastServerIndexPlus):
            currServer = self.serversStats[s]
            for stat in currServer.keys():
                value = currServer[stat]
                m = value['mean']
                variance = value['variance']
                std_dev = value['stdev']
                interval = value['confidence_interval_length'] 
                string += f'{num},{stat}_server{s},{m:.3f},{variance:.3f},{std_dev:.3f},{interval:.3f}\n'
        return string
        

    def append(self, newEvent:SamplingEvent):
        if config.DEBUG:
            print('NEW EVENT')
            print(newEvent)
            print('\n')
        type = newEvent.type
        num = None
        if type == 0:
            self.sampleListB.append(newEvent)
            self.numSampleB += 1
            # used in welford algho
            num = self.numSampleB
            self.processedJobs[0] = newEvent.processedJobs
        else:
            self.sampleListP.append(newEvent)
            self.numSampleP += 1
            # used in welford algho
            num = self.numSampleP
            self.processedJobs[1] = newEvent.processedJobs
            
        # one pass algho for each statistic:
        mean = self.avgInterarrivals[type]['mean']
        diff = newEvent.avgInterarrivals - mean
        wel = self.welfordNextStep(diff, num)
        self.avgInterarrivals[type]['mean'] += wel[0]
        self.avgInterarrivals[type]['variance'] += wel[1]
        """ if self.computeAutocorrelation and num > config.LAG_J:
            self.avgInterarrivals[type]['autocorrelation'] += newEvent.avgInterarrivals * list[num - 1 - config.LAG_J].avgInterarrivals """
           
        mean = self.avgWaits[type]['mean']
        diff = newEvent.avgWaits - mean
        wel = self.welfordNextStep(diff, num)
        self.avgWaits[type]['mean'] += wel[0]
        self.avgWaits[type]['variance'] += wel[1]
        """ if self.computeAutocorrelation and num > config.LAG_J:
            self.avgWaits[type]['autocorrelation'] += newEvent.avgWaits * list[num - 1 - config.LAG_J].avgWaits """

        mean = self.avgNumNodes[type]['mean']
        diff = newEvent.avgNumNodes - mean
        wel = self.welfordNextStep(diff, num)
        self.avgNumNodes[type]['mean'] += wel[0]
        self.avgNumNodes[type]['variance'] += wel[1]
        """ if self.computeAutocorrelation and num > config.LAG_J:
            self.avgNumNodes[type]['autocorrelation'] += newEvent.avgNumNodes * list[num - 1 - config.LAG_J].avgNumNodes """

        mean = self.avgDelays[type]['mean']
        diff = newEvent.avgDelays - mean
        wel = self.welfordNextStep(diff, num)
        self.avgDelays[type]['mean'] += wel[0]
        self.avgDelays[type]['variance'] += wel[1]
        """ if self.computeAutocorrelation and num > config.LAG_J:
            self.avgDelays[type]['autocorrelation'] += newEvent.avgDelays * list[num - 1 - config.LAG_J].avgDelays """


        mean = self.avgNumQueues[type]['mean']
        diff = newEvent.avgNumQueues - mean
        wel = self.welfordNextStep(diff, num)
        self.avgNumQueues[type]['mean'] += wel[0]
        self.avgNumQueues[type]['variance'] += wel[1]
        """ if self.computeAutocorrelation and num > config.LAG_J:
            self.avgNumQueues[type]['autocorrelation'] += newEvent.avgNumQueues * list[num - 1 - config.LAG_J].avgNumQueues """



        # newEvent.avgServersStas is a list of dic: [0: b_servers, 1: p_servers]
        
        newSampleServersKind = newEvent.avgServersStats
        
        # for each server of that kind
        for s in newSampleServersKind.keys():
            # in self.serversStats, all servers are kept together. take the correct one by its index    
            averaged = self.serversStats[s]
            # take the new stats relative to the same server
            currNewServer = newSampleServersKind[s]
            #currMinusJ = list[num - 1 - config.LAG_J].avgServersStats
            # for each statistic (utilization, service and share)
            for statistic in currNewServer.keys():
                mean = averaged[statistic]['mean']
                diff = currNewServer[statistic] - mean
                wel = self.welfordNextStep(diff, num)
                self.serversStats[s][statistic]['mean'] += wel[0]
                self.serversStats[s][statistic]['variance'] += wel[1]
                """ if self.computeAutocorrelation and num > config.LAG_J:
                    self.serversStats[s][statistic]['autocorrelation'] += currNewServer[statistic] * currMinusJ[s][statistic] """

   
    def welfordNextStep(self, diff:float, num:int):
        # num is passed as param because its not know at the beginnig if is P or B event
        mean = diff / num
        variance = diff * diff * (num - 1) / num
        return [mean, variance]

    def makeCorrectVariance(self, alsoP=False):
        """ in welford algho, the variance has to be divided by the sample size in the end
        in order to obtain the correct std dev. here i'm going to divide by the sample size
        all the std devs: """
        iterations = 1
        if (alsoP):
            iterations = 2

        # print('\n\n\n', self)
        # input()
        num = self.numSampleB
        for i in range(iterations): # both the b and p type
            self.avgInterarrivals[i]['variance'] /= num
            self.avgInterarrivals[i]['stdev'] = sqrt(self.avgInterarrivals[i]['variance'])

            self.avgWaits[i]['variance'] /= num
            self.avgWaits[i]['stdev'] = sqrt(self.avgWaits[i]['variance'])

            self.avgNumNodes[i]['variance'] /= num
            self.avgNumNodes[i]['stdev'] = sqrt(self.avgNumNodes[i]['variance'])

            self.avgDelays[i]['variance'] /= num
            self.avgDelays[i]['stdev'] = sqrt(self.avgDelays[i]['variance'])

            self.avgNumQueues[i]['variance'] /= num
            self.avgNumQueues[i]['stdev'] = sqrt(self.avgNumQueues[i]['variance'])
            
            num = self.numSampleP

        for s in self.serversStats.keys():
            curr_server = self.serversStats[s]
            for statistic in curr_server.keys():
                if s in range(1, config.SERVERS_B + 1):
                    num = self.numSampleB
                else:
                    if not alsoP:
                        continue
                    num = self.numSampleP
                curr_server[statistic]['variance'] /= num
                curr_server[statistic]['stdev'] = sqrt(curr_server[statistic]['variance'])


    
    def computeAutocorrelation(self, alsoP = False):
        # self.avgInterarrivals B
        l = [i.avgInterarrivals for i in self.sampleListB]
        mean = self.avgInterarrivals[0]['mean']
        variance = self.avgInterarrivals[0]['variance']
        self.avgInterarrivals[0]['autocorrelation'] = computeAutocorrelation(l, mean, variance)

        # self.avgWaits 
        l = [i.avgWaits for i in self.sampleListB]
        mean = self.avgWaits[0]['mean']
        variance = self.avgWaits[0]['variance']
        self.avgWaits[0]['autocorrelation'] = computeAutocorrelation(l, mean, variance)


        # self.avgNumNodes
        l = [i.avgNumNodes for i in self.sampleListB]
        mean = self.avgNumNodes[0]['mean']
        variance = self.avgNumNodes[0]['variance']
        self.avgNumNodes[0]['autocorrelation'] = computeAutocorrelation(l, mean, variance)

        # self.avgDelays 
        l = [i.avgDelays for i in self.sampleListB]
        mean = self.avgDelays[0]['mean']
        variance = self.avgDelays[0]['variance']
        self.avgDelays[0]['autocorrelation'] = computeAutocorrelation(l, mean, variance)
        
        # self.avgNumQueues
        l = [i.avgNumQueues for i in self.sampleListB]
        mean = self.avgNumQueues[0]['mean']
        variance = self.avgNumQueues[0]['variance']
        self.avgNumQueues[0]['autocorrelation'] = computeAutocorrelation(l, mean, variance)

        # self.avgServer:
        for s in range(1, config.SERVERS_B + 1):
            for statistic in self.serversStats[s].keys():
                mean = self.serversStats[s][statistic]['mean']
                variance = self.serversStats[s][statistic]['variance']
                l = [i.avgServersStats[s][statistic] for i in self.sampleListB]
                self.serversStats[s][statistic]['autocorrelation'] = computeAutocorrelation(l, mean, variance)


        if alsoP:
            # self.avgInterarrivals P
            l = [i.avgInterarrivals for i in self.sampleListP]
            mean = self.avgInterarrivals[1]['mean']
            variance = self.avgInterarrivals[1]['variance']
            self.avgInterarrivals[1]['autocorrelation'] = computeAutocorrelation(l, mean, variance)

            # self.avgWaits 
            l = [i.avgWaits for i in self.sampleListP]
            mean = self.avgWaits[1]['mean']
            variance = self.avgWaits[1]['variance']
            self.avgWaits[1]['autocorrelation'] = computeAutocorrelation(l, mean, variance)


            # self.avgNumNodes
            l = [i.avgNumNodes for i in self.sampleListP]
            mean = self.avgNumNodes[1]['mean']
            variance = self.avgNumNodes[1]['variance']
            self.avgNumNodes[1]['autocorrelation'] = computeAutocorrelation(l, mean, variance)

            # self.avgDelays 
            l = [i.avgDelays for i in self.sampleListP]
            mean = self.avgDelays[1]['mean']
            variance = self.avgDelays[1]['variance']
            self.avgDelays[1]['autocorrelation'] = computeAutocorrelation(l, mean, variance)
            
            # self.avgNumQueues
            l = [i.avgNumQueues for i in self.sampleListP]
            mean = self.avgNumQueues[1]['mean']
            variance = self.avgNumQueues[1]['variance']
            self.avgNumQueues[1]['autocorrelation'] = computeAutocorrelation(l, mean, variance)

            # self.avgServer:
            for s in range(config.SERVERS_B + 2, config.SERVERS_B + 2 + config.SERVERS_P):
                for statistic in self.serversStats[s].keys():
                    mean = self.serversStats[s][statistic]['mean']
                    variance = self.serversStats[s][statistic]['variance']
                    l = [i.avgServersStats[s][statistic] for i in self.sampleListP]
                    self.serversStats[s][statistic]['autocorrelation'] = computeAutocorrelation(l, mean, variance)

    def evaluateAutocorrelation(self) -> bool:
        l = []
        for i in range(2): # both the b and p type
            l.append(self.avgInterarrivals[i]['autocorrelation'])
            l.append(self.avgWaits[i]['autocorrelation'])
            l.append(self.avgNumNodes[i]['autocorrelation'])
            l.append(self.avgDelays[i]['autocorrelation'])
            l.append(self.avgNumQueues[i]['autocorrelation'])

        for s in self.serversStats.keys():
            curr_server = self.serversStats[s]
            l.append(curr_server['service']['autocorrelation']) 
        
        if config.DEBUG:
            print(f'l = {l}')
            print(f'will restart? {not all(abs(val) < config.AUTOCORR_THRESHOLD for val in l)}')

        return all(abs(val) < config.AUTOCORR_THRESHOLD for val in l)

    def computeConfidenceInterval(self, confidenceLevel, alsoP=False):
        # confidence level is 1 - a
        alpha = 1 - confidenceLevel
        iterations = 1
        if (alsoP):
            iterations = 2

        num = self.numSampleB
        for i in range(iterations): # both the b and p type
            
            self.setIntervalLegth(self.avgInterarrivals[i], num, alpha)
            self.setIntervalLegth(self.avgWaits[i], num, alpha)
            self.setIntervalLegth(self.avgNumNodes[i], num, alpha)
            self.setIntervalLegth(self.avgDelays[i], num, alpha)
            self.setIntervalLegth(self.avgNumQueues[i], num, alpha)
            
            num = self.numSampleP

        for s in self.serversStats.keys():
            curr_server = self.serversStats[s]
            for statistic in curr_server.keys():
                if s in range(1, config.SERVERS_B + 1):
                    num = self.numSampleB
                else:
                    if not alsoP:
                        continue
                    num = self.numSampleP
                
                self.setIntervalLegth(curr_server[statistic], num, alpha)


    def setIntervalLegth(self, statisticDict:dict, num:int, alpha:float):
        u = 1 - alpha * 0.5
        t = idfStudent(num - 1, u)
        stdev = statisticDict['stdev'] 
        if stdev == 0: # not yet computed:
            stdev = sqrt(statisticDict['variance'] / num)
        w = t * stdev / sqrt(num - 1)
        statisticDict['confidence_interval_length'] = w


    def merge(self, otherSamplingList:'SamplingList'):
        outputList = SamplingList()

        # commented out since useless right now
        # outputList.sampleListB = deepcopy(self.sampleListB) + deepcopy(otherSamplingList.sampleListB)
        # outputList.sampleListP = deepcopy(otherSamplingList.sampleListP)
        
        firstHalfProcessedJobs = self.processedJobs[0]
        secondHalfProcessedJobs = otherSamplingList.processedJobs[0]
        totalJobs = firstHalfProcessedJobs + secondHalfProcessedJobs

        # all the p type requests are stored into the second half
        outputList.processedJobs = [totalJobs, otherSamplingList.processedJobs[1]]
        outputList.numSampleB = self.numSampleB + otherSamplingList.numSampleB
        outputList.numSampleP = otherSamplingList.numSampleP
        
        firstHalfMean = self.avgInterarrivals[0]['mean']
        secondHalfMean = otherSamplingList.avgInterarrivals[0]['mean']
        outputList.avgInterarrivals[0]['mean'] = firstHalfMean * firstHalfProcessedJobs +\
             secondHalfMean * secondHalfProcessedJobs
        outputList.avgInterarrivals[0]['mean'] /= totalJobs

        firstHalfVariance = self.avgInterarrivals[0]['variance']
        secondHalfVariance = otherSamplingList.avgInterarrivals[0]['variance']
        outputList.avgInterarrivals[0]['variance'] = firstHalfVariance * firstHalfProcessedJobs +\
             secondHalfVariance * secondHalfProcessedJobs
        outputList.avgInterarrivals[0]['variance'] /= totalJobs

        
        firstHalfMean = self.avgWaits[0]['mean']
        secondHalfMean = otherSamplingList.avgWaits[0]['mean']
        outputList.avgWaits[0]['mean'] = firstHalfMean * firstHalfProcessedJobs + \
            secondHalfMean * secondHalfProcessedJobs
        outputList.avgWaits[0]['mean'] /= totalJobs

        firstHalfVariance = self.avgWaits[0]['variance']
        secondHalfVariance = otherSamplingList.avgWaits[0]['variance']
        outputList.avgWaits[0]['variance'] = firstHalfVariance * firstHalfProcessedJobs +\
             secondHalfVariance * secondHalfProcessedJobs
        outputList.avgWaits[0]['variance'] /= totalJobs



        firstHalfMean = self.avgNumNodes[0]['mean']
        secondHalfMean = otherSamplingList.avgNumNodes[0]['mean']
        outputList.avgNumNodes[0]['mean'] = firstHalfMean * firstHalfProcessedJobs + \
            secondHalfMean * secondHalfProcessedJobs
        outputList.avgNumNodes[0]['mean'] /= totalJobs

        firstHalfVariance = self.avgNumNodes[0]['variance']
        secondHalfVariance = otherSamplingList.avgNumNodes[0]['variance']
        outputList.avgNumNodes[0]['variance'] = firstHalfVariance * firstHalfProcessedJobs +\
             secondHalfVariance * secondHalfProcessedJobs
        outputList.avgNumNodes[0]['variance'] /= totalJobs



        firstHalfMean = self.avgDelays[0]['mean']
        secondHalfMean = otherSamplingList.avgDelays[0]['mean']
        outputList.avgDelays[0]['mean'] = firstHalfMean * firstHalfProcessedJobs + \
            secondHalfMean * secondHalfProcessedJobs
        outputList.avgDelays[0]['mean'] /= totalJobs

        firstHalfVariance = self.avgDelays[0]['variance']
        secondHalfVariance = otherSamplingList.avgDelays[0]['variance']
        outputList.avgDelays[0]['variance'] = firstHalfVariance * firstHalfProcessedJobs +\
             secondHalfVariance * secondHalfProcessedJobs
        outputList.avgDelays[0]['variance'] /= totalJobs




        firstHalfMean = self.avgNumQueues[0]['mean']
        secondHalfMean = otherSamplingList.avgNumQueues[0]['mean']
        outputList.avgNumQueues[0]['mean'] = firstHalfMean * firstHalfProcessedJobs + \
            secondHalfMean * secondHalfProcessedJobs
        outputList.avgNumQueues[0]['mean'] /= totalJobs

        firstHalfVariance = self.avgNumQueues[0]['variance']
        secondHalfVariance = otherSamplingList.avgNumQueues[0]['variance']
        outputList.avgNumQueues[0]['variance'] = firstHalfVariance * firstHalfProcessedJobs +\
             secondHalfVariance * secondHalfProcessedJobs
        outputList.avgNumQueues[0]['variance'] /= totalJobs


        # copy P-value from second 8 hrs 
        outputList.avgInterarrivals[1] = deepcopy(otherSamplingList.avgInterarrivals[1])
        outputList.avgWaits[1] = deepcopy(otherSamplingList.avgWaits[1])
        outputList.avgNumNodes[1] = deepcopy(otherSamplingList.avgNumNodes[1])
        outputList.avgDelays[1] = deepcopy(otherSamplingList.avgDelays[1])
        outputList.avgNumQueues[1] = deepcopy(otherSamplingList.avgNumQueues[1])


        firstServerIndexes = list(range(1, config.SERVERS_B + 1))

        # for each server 
        for s in self.serversStats.keys():
            if s not in firstServerIndexes:
                outputList.serversStats[s] = deepcopy(otherSamplingList.serversStats[s])
            else:
                for statistic in self.serversStats[s]:
                    firstHalfMean = self.serversStats[s][statistic]['mean']
                    secondHalfMean = otherSamplingList.serversStats[s][statistic]['mean']
                    outputList.serversStats[s][statistic]['mean'] = \
                        firstHalfMean * firstHalfProcessedJobs + \
                        secondHalfMean * secondHalfProcessedJobs

                    outputList.serversStats[s][statistic]['mean'] /= totalJobs

        return outputList