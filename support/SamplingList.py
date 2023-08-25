from support.SamplingEvent import SamplingEvent

from configurations.Config import config

def makeDict():
    d = dict()
    d['mean'] = 0
    d['variance'] = 0
    d['autocorrelation'] = 0
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
    # computeAutocorrelation = None


    def __init__(self):
        #self. computeAutocorrelation = computeAutocorr

        self.sampleListB = []
        self.sampleListP = []

        self.avgInterarrivals = [makeDict(), makeDict()]
        self.avgWaits = [makeDict(), makeDict()]
        self.avgNumNodes = [makeDict(), makeDict()]
        self.avgDelays = [makeDict(), makeDict()]
        self.avgNumQueues = [makeDict(), makeDict()]
        self.serversStats = dict()
        for s in list(range(1, config.SERVERS_B + 1)) + list(range(config.SERVERS_B + 2, config.SERVERS_B + 2 + config.SERVERS_P)):
    
            self.serversStats[s] = dict()
            self.serversStats[s]['utilization'] = dict()
            self.serversStats[s]['service'] = dict()
            self.serversStats[s]['share'] = dict()

            self.serversStats[s]['utilization']['mean'] = 0
            self.serversStats[s]['utilization']['variance'] = 0
            self.serversStats[s]['utilization']['autocorrelation'] = 0

            self.serversStats[s]['service']['mean'] = 0
            self.serversStats[s]['service']['variance'] = 0
            self.serversStats[s]['service']['autocorrelation'] = 0

            self.serversStats[s]['share']['mean'] = 0
            self.serversStats[s]['share']['variance'] = 0
            self.serversStats[s]['share']['autocorrelation'] = 0


    def __str__(self) -> str:
        my_str = f'numSampleB: {self.numSampleB}\nnumSampleP: {self.numSampleP}\n'
        titles = ['BAR', 'PIZZERIA']
        
        for attr, value in vars(self).items():
            if attr in ('sampleListB', 'serversStats', 'sampleListP', 'numSampleB', 'numSampleP', 'computeAutocorrelation'):
                    continue
            for i in range(2):
                m = value[i]['mean']
                variance = value[i]['variance']
                autocorr = value[i]['autocorrelation']
                my_str += f'{attr}_{titles[i]} -- mean: {m}, variance: {variance} -- autocorr: {autocorr}\n'
    
        for s in self.serversStats.keys():
            my_str += f'server {s}\n'
            m = self.serversStats[s]['utilization']['mean']
            variance = self.serversStats[s]['utilization']['variance']
            autocorr = self.serversStats[s]['utilization']['autocorrelation']
            my_str += f'\tutilization -- mean {m} -- variance {variance} -- autocorr: {autocorr}\n'

            m = self.serversStats[s]['service']['mean']
            variance = self.serversStats[s]['service']['variance']
            autocorr = self.serversStats[s]['service']['autocorrelation']
            my_str += f'\tservice -- mean {m} -- variance {variance} -- autocorr: {autocorr}\n'

            m = self.serversStats[s]['share']['mean']
            variance = self.serversStats[s]['share']['variance']
            autocorr = self.serversStats[s]['share']['autocorrelation']
            my_str += f'\tshare -- mean {m} -- variance {variance} -- autocorr: {autocorr}\n'

        return my_str
    
    def append(self, newEvent:SamplingEvent):
        type = newEvent.type
        num = None
        list = None
        if type == 0:
            self.sampleListB.append(newEvent)
            self.numSampleB += 1
            # used in welford algho
            num = self.numSampleB
            list = self.sampleListB
        else:
            self.sampleListP.append(newEvent)
            self.numSampleP += 1
            # used in welford algho
            num = self.numSampleP
            list = self.sampleListP
            
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
            self.avgWaits[i]['variance'] /= num
            self.avgNumNodes[i]['variance'] /= num
            self.avgDelays[i]['variance'] /= num
            self.avgNumQueues[i]['variance'] /= num
            
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

        return all(abs(val) < config.AUTOCORR_THRESHOLD for val in l)
