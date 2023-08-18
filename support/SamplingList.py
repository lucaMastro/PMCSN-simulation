from support.SamplingEvent import SamplingEvent

from configurations.Config import config

def makeDict():
    d = dict()
    d['mean'] = 0
    d['std_dev'] = 0
    return d


class SamplingList:

    # list of objects SamplingEvent
    sampleListB = None
    sampleListP = None
    numSampleB = 0
    numSampleP = 0

    """ those statistics will keep mean and std_dev for both cases B and P. they are list of 2 dict:
     ------------------B_DICT-------------,   ------------------P_DICT-------------
    [{'mean' = xi, 'std_dev' = (xj - xi)^2}, {'mean' = xi, 'std_dev' = (xj - xi)^2}]
    
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
              'std_dev': 0    
          }
          'service': {
              'mean': 0,
              'std_dev' = 0
          }
          'share': {
              'mean': 0,
              'std_dev' = 0
          }
      }
    }
    """
    serversStats = None


    def __init__(self):
        self.sampleListB = []
        self.sampleListP = []

        self.avgInterarrivals = [makeDict(), makeDict()]
        self.avgWaits = [makeDict(), makeDict()]
        self.avgNumNodes = [makeDict(), makeDict()]
        self.avgDelays = [makeDict(), makeDict()]
        self.avgNumQueues = [makeDict(), makeDict()]
        self.serversStats = dict()
        for s in range(1, config.SERVERS_B + 1):
            self.serversStats[s] = dict()
            self.serversStats[s]['utilization'] = dict()
            self.serversStats[s]['service'] = dict()
            self.serversStats[s]['share'] = dict()

            self.serversStats[s]['utilization']['mean'] = 0
            self.serversStats[s]['service']['mean'] = 0
            self.serversStats[s]['share']['mean'] = 0
            self.serversStats[s]['utilization']['std_dev'] = 0
            self.serversStats[s]['service']['std_dev'] = 0
            self.serversStats[s]['share']['std_dev'] = 0
        
        for s in range(config.SERVERS_B + 2, config.SERVERS_B + 2 + config.SERVERS_P):
            self.serversStats[s] = dict()
            self.serversStats[s]['utilization'] = dict()
            self.serversStats[s]['service'] = dict()
            self.serversStats[s]['share'] = dict()

            self.serversStats[s]['utilization']['mean'] = 0
            self.serversStats[s]['service']['mean'] = 0
            self.serversStats[s]['share']['mean'] = 0
            self.serversStats[s]['utilization']['std_dev'] = 0
            self.serversStats[s]['service']['std_dev'] = 0
            self.serversStats[s]['share']['std_dev'] = 0

    def __str__(self) -> str:
        my_str = f'numSampleB: {self.numSampleB}\nnumSampleP: {self.numSampleP}\n'
        titles = ['BAR', 'PIZZERIA']
        
        for attr, value in vars(self).items():
            print(attr)
            if attr in ('sampleListB', 'serversStats', 'sampleListP', 'numSampleB', 'numSampleP'):
                    continue
            for i in range(2):
                m = value[i]['mean']
                std_dev = value[i]['std_dev']
                my_str += f'{attr}_{titles[i]} -- mean: {m}, std_dev: {std_dev}\n'
    
        for s in self.serversStats.keys():
            my_str += f'server {s}\n'
            m = self.serversStats[s]['utilization']['mean']
            std_dev = self.serversStats[s]['utilization']['std_dev']
            my_str += f'\tutilization -- mean {m} -- std_dev {std_dev}\n'

            m = self.serversStats[s]['service']['mean']
            std_dev = self.serversStats[s]['service']['std_dev']
            my_str += f'\tservice -- mean {m} -- std_dev {std_dev}\n'

            m = self.serversStats[s]['share']['mean']
            std_dev = self.serversStats[s]['share']['std_dev']
            my_str += f'\tshare -- mean {m} -- std_dev {std_dev}\n'

        return my_str
    
    def append(self, newEvent:SamplingEvent):
        type = newEvent.type
        num = None
        if type == 0:
            self.sampleListB.append(newEvent)
            self.numSampleB += 1
            # used in welford algho
            num = self.numSampleB
        else:
            self.sampleListP.append(newEvent)
            self.numSampleP += 1
            # used in welford algho
            num = self.numSampleP
            
        # one pass algho for each statistic:
        mean = self.avgInterarrivals[type]['mean']
        diff = newEvent.avgInterarrivals - mean
        wel = self.welfordNextStep(diff, num)
        self.avgInterarrivals[type]['mean'] += wel[0]
        self.avgInterarrivals[type]['std_dev'] += wel[1]

        mean = self.avgWaits[type]['mean']
        """  print(f'mean:{mean}')
        print(f'eventWait = {newEvent.avgWaits[0]}') """
        diff = newEvent.avgWaits - mean
        wel = self.welfordNextStep(diff, num)
        self.avgWaits[type]['mean'] += wel[0]
        self.avgWaits[type]['std_dev'] += wel[1]

        mean = self.avgNumNodes[type]['mean']
        diff = newEvent.avgNumNodes - mean
        wel = self.welfordNextStep(diff, num)
        self.avgNumNodes[type]['mean'] += wel[0]
        self.avgNumNodes[type]['std_dev'] += wel[1]

        mean = self.avgDelays[type]['mean']
        diff = newEvent.avgDelays - mean
        wel = self.welfordNextStep(diff, num)
        self.avgDelays[type]['mean'] += wel[0]
        self.avgDelays[type]['std_dev'] += wel[1]


        mean = self.avgNumQueues[type]['mean']
        diff = newEvent.avgNumQueues - mean
        wel = self.welfordNextStep(diff, num)
        self.avgNumQueues[type]['mean'] += wel[0]
        self.avgNumQueues[type]['std_dev'] += wel[1]



        # newEvent.avgServersStas is a list of dic: [0: b_servers, 1: p_servers]
        
        newSampleServersKind = newEvent.avgServersStats
        
        # for each server of that kind
        for s in newSampleServersKind.keys():
            # in self.serversStats, all servers are kept together. take the correct one by its index    
            averaged = self.serversStats[s]
            # take the new stats relative to the same server
            currNewServer = newSampleServersKind[s]

            # for each statistic (utilization, service and share)
            for statistic in currNewServer.keys():
                mean = averaged[statistic]['mean']
                diff = currNewServer[statistic] - mean
                wel = self.welfordNextStep(diff, num)
                self.serversStats[s][statistic]['mean'] += wel[0]
                self.serversStats[s][statistic]['std_dev'] += wel[1]

   
    def welfordNextStep(self, diff:float, num:int):
        # num is passed as param because its not know at the beginnig if is P or B event
        mean = diff / num
        std_dev = diff * diff * (num - 1) / num
        return [mean, std_dev]

    def makeCorrectStdDev(self):
        """ in welford algho, the std dev has to be divided by the sample size in the end
        in order to obtain the correct std dev. here i'm going to divide by the sample size
        all the std devs: """
        num = self.numSampleB
        for i in range(2): # both the b and p type
            self.avgInterarrivals[i]['std_dev'] /= num
            self.avgWaits[i]['std_dev'] /= num
            self.avgNumNodes[i]['std_dev'] /= num
            self.avgDelays[i]['std_dev'] /= num
            self.avgNumQueues[i]['std_dev'] /= num
            num = self.numSampleP

        for s in self.serversStats.keys():
            curr_server = self.serversStats[s]
            for statistic in curr_server.keys():
                if s in range(1, config.SERVERS_B + 1):
                    num = self.numSampleB
                else:
                    num = self.numSampleP
                curr_server[statistic]['std_dev'] /= num
