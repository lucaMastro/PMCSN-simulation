from support.SamplingEvent import SamplingEvent

from support.Config import config

def makeDict():
    d = dict()
    d['mean'] = 0
    d['std_dev'] = 0
    return d


class SamplingList:

    # list of objects SamplingEvent
    sampleList = None
    numSample = 0

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
        self.sampleList = []

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
        my_str = ''
        titles = ['BAR', 'PIZZERIA']
        try:
            for attr, value in vars(self).items():
                if attr == 'sampleList':
                        continue
                for i in range(2):
                    m = value[i]['mean']
                    std_dev = value[i]['std_dev']
                    my_str += f'{attr}_{titles[i]} -- mean: {m}, std_dev: {std_dev}\n'
        except:
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
        self.sampleList.append(newEvent)
        self.numSample += 1

        # one pass algho for each statistic:
        mean = self.avgInterarrivals[0]['mean']
        diff = newEvent.avgInterarrivals[0] - mean
        wel = self.welfordNextStep(diff)
        self.avgInterarrivals[0]['mean'] += wel[0]
        self.avgInterarrivals[0]['std_dev'] += wel[1]

        mean = self.avgInterarrivals[1]['mean']
        diff = newEvent.avgInterarrivals[1] - mean
        wel = self.welfordNextStep(diff)
        self.avgInterarrivals[1]['mean'] += wel[0]
        self.avgInterarrivals[1]['std_dev'] += wel[1]

        mean = self.avgWaits[0]['mean']
        """  print(f'mean:{mean}')
        print(f'eventWait = {newEvent.avgWaits[0]}') """
        diff = newEvent.avgWaits[0] - mean
        wel = self.welfordNextStep(diff)
        self.avgWaits[0]['mean'] += wel[0]
        self.avgWaits[0]['std_dev'] += wel[1]

        mean = self.avgWaits[1]['mean']
        diff = newEvent.avgWaits[1] - mean
        wel = self.welfordNextStep(diff)
        self.avgWaits[1]['mean'] += wel[0]
        self.avgWaits[1]['std_dev'] += wel[1]

        mean = self.avgNumNodes[0]['mean']
        diff = newEvent.avgNumNodes[0] - mean
        wel = self.welfordNextStep(diff)
        self.avgNumNodes[0]['mean'] += wel[0]
        self.avgNumNodes[0]['std_dev'] += wel[1]

        mean = self.avgNumNodes[1]['mean']
        diff = newEvent.avgNumNodes[1] - mean
        wel = self.welfordNextStep(diff)
        self.avgNumNodes[1]['mean'] += wel[0]
        self.avgNumNodes[1]['std_dev'] += wel[1]

        mean = self.avgDelays[0]['mean']
        diff = newEvent.avgDelays[0] - mean
        wel = self.welfordNextStep(diff)
        self.avgDelays[0]['mean'] += wel[0]
        self.avgDelays[0]['std_dev'] += wel[1]

        mean = self.avgDelays[1]['mean']
        diff = newEvent.avgDelays[1] - mean
        wel = self.welfordNextStep(diff)
        self.avgDelays[1]['mean'] += wel[0]
        self.avgDelays[1]['std_dev'] += wel[1]

        mean = self.avgNumQueues[0]['mean']
        diff = newEvent.avgNumQueues[0] - mean
        wel = self.welfordNextStep(diff)
        self.avgNumQueues[0]['mean'] += wel[0]
        self.avgNumQueues[0]['std_dev'] += wel[1]

        mean = self.avgNumQueues[1]['mean']
        diff = newEvent.avgNumQueues[1] - mean
        wel = self.welfordNextStep(diff)
        self.avgNumQueues[1]['mean'] += wel[0]
        self.avgNumQueues[1]['std_dev'] += wel[1]


        # newEvent.avgServersStas is a list of dic: [0: b_servers, 1: p_servers]
        for pb_index in range(2):
            newSampleServersKind = newEvent.avgServersStats[pb_index]
            
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
                    wel = self.welfordNextStep(diff)
                    self.serversStats[s][statistic]['mean'] += wel[0]
                    self.serversStats[s][statistic]['std_dev'] += wel[1]

   
    def welfordNextStep(self, diff:float):
        mean = diff / self.numSample
        std_dev = diff * diff * (self.numSample - 1) / self.numSample
        return [mean, std_dev]

    def makeCorrectStdDev(self):
        """ in welford algho, the std dev has to be divided by the sample size in the end
        in order to obtain the correct std dev. here i'm going to divide by the sample size
        all the std devs: """
        for i in range(2): # both the b and p type
            self.avgInterarrivals[i]['std_dev'] /= self.numSample
            self.avgWaits[i]['std_dev'] /= self.numSample
            self.avgNumNodes[i]['std_dev'] /= self.numSample
            self.avgDelays[i]['std_dev'] /= self.numSample
            self.avgNumQueues[i]['std_dev'] /= self.numSample

        for s in self.serversStats.keys():
            curr_server = self.serversStats[s]
            for statistic in curr_server.keys():
                curr_server[statistic]['std_dev'] /= self.numSample
