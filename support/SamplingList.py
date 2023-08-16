from support.SamplingEvent import SamplingEvent
import support.Config as config

def makeDict():
    d = dict()
    d['mean'] = 0
    d['std_dev'] = 0
    return d


class SamplingList:

    # list of objects SamplingEvent
    sampleList = None
    numSample = 0

    # those statistics will keep mean and std_dev for both cases B and P. they are list of 2 dict:
    #  ------------------B_DICT-------------,   ------------------P_DICT-------------
    # [{'mean' = xi, 'std_dev' = (xj - xi)^2}, {'mean' = xi, 'std_dev' = (xj - xi)^2}]
    #
    # the above statistics are computed with welford one-pass algho
    avgInterarrivals = None
    avgWaits = None
    avgNumNodes = None
    avgDelays = None
    avgNumQueues = None
    serversStats = None


    def __init__(self):
        self.sampleList = []

        self.avgInterarrivals = [makeDict(), makeDict()]
        self.avgWaits = [makeDict(), makeDict()]
        self.avgNumNodes = [makeDict(), makeDict()]
        self.avgDelays = [makeDict(), makeDict()]
        self.avgNumQueues = [makeDict(), makeDict()]
        self.serversStats = [makeDict(), makeDict()]


    
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

        mean = self.self.avgWaits[0]['mean']
        diff = newEvent.self.avgWaits[0] - mean
        wel = self.welfordNextStep(diff)
        self.self.avgWaits[0]['mean'] += wel[0]
        self.self.avgWaits[0]['std_dev'] += wel[1]

        mean = self.self.avgWaits[1]['mean']
        diff = newEvent.self.avgWaits[1] - mean
        wel = self.welfordNextStep(diff)
        self.self.avgWaits[1]['mean'] += wel[0]
        self.self.avgWaits[1]['std_dev'] += wel[1]

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

        mean = self.serversStats[0]['mean']
        diff = newEvent.serversStats[0] - mean
        wel = self.welfordNextStep(diff)
        self.serversStats[0]['mean'] += wel[0]
        self.serversStats[0]['std_dev'] += wel[1]

        mean = self.serversStats[1]['mean']
        diff = newEvent.serversStats[1] - mean
        wel = self.welfordNextStep(diff)
        self.serversStats[1]['mean'] += wel[0]
        self.serversStats[1]['std_dev'] += wel[1]


   
    def welfordNextStep(self, diff:float):
        mean = diff / self.numSample
        std_dev = diff * diff * (self.numSample - 1) / self.numSample
        return [mean, std_dev]

