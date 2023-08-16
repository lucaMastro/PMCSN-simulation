from support.Time import Time
from support.Statistics import Statistics
import support.Config as config

def computeAvgInterarrivals(stats:Statistics, kindP=False):
    lastArrivalTime = None
    processedJobs = None
    if not kindP:
        lastArrivalTime = stats.events[0].t  
        processedJobs = stats.processedJobs[0]
    else:
        lastArrivalTime = stats.events[config.SERVERS_B + 1].t
        processedJobs = stats.processedJobs[1]
    return lastArrivalTime / processedJobs

def computeAvgWait(stats:Statistics, kindP=False):
    area = None
    processedJobs = None
    if not kindP:
        area = stats.areas[0]  
        processedJobs = stats.processedJobs[0]
    else:
        area = stats.areas[1]  
        processedJobs = stats.processedJobs[1]
    return area / processedJobs
    
def computeAvgNumNode(stats:Statistics, time:Time, kindP=False):
    area = stats.areas[0] if not kindP else stats.areas[1]
    return area / time.current

def computeAvgDelay(stats:Statistics, kindP=False):
    # get area to adjust:
    area = None
    procesedJobs = None
    firstServerIndex = None
    # the following keep lastServerIndex + 1. It's the right extreme of for cycle
    lastServerIndexPlus = None
    if not kindP:
        area = stats.areas[0]
        firstServerIndex = 1
        lastServerIndexPlus = config.SERVERS_B + 1
        procesedJobs = stats.processedJobs[0]
    else:
        area = stats.areas[1]
        firstServerIndex = config.SERVERS_B + 2
        lastServerIndexPlus = config.SERVERS_B + 2 + config.SERVERS_P
        procesedJobs = stats.processedJobs[1]
    
    #adjust area
    for s in range(firstServerIndex, lastServerIndexPlus):
            area -= stats.sum[s].service
    
    return area / procesedJobs



def computeAvgNumQueue(stats:Statistics, time:Time, kindP=False):
    # get area to adjust:
    area = None
    firstServerIndex = None
    # the following keep lastServerIndex + 1. It's the right extreme of for cycle
    lastServerIndexPlus = None
    
    if not kindP:
        area = stats.areas[0]
        firstServerIndex = 1
        lastServerIndexPlus = config.SERVERS_B + 1
        
    else:
        area = stats.areas[1]
        firstServerIndex = config.SERVERS_B + 2
        lastServerIndexPlus = config.SERVERS_B + 2 + config.SERVERS_P
    
    #adjust area
    for s in range(firstServerIndex, lastServerIndexPlus):
            area -= stats.sum[s].service
    return area / time.current


def computeAvgServerStats(stats:Statistics, time:Time, kindP=False):
    # server stats are utilization, service, share. They are kept in a dict of dict:
    # {
    #   s: {
    #       'utilization': 0
    #       'service': 0
    #       'share': 0
    #   }
    # }
    #
    ext_dict = dict()
    firstServerIndex = None
    # the following keep lastServerIndex + 1. It's the right extreme of for cycle
    lastServerIndexPlus = None
    processedJobs = None
    if not kindP:
        firstServerIndex = 1
        lastServerIndexPlus = config.SERVERS_B + 1
        processedJobs = stats.processedJobs[0]
    else:
        firstServerIndex = config.SERVERS_B + 2
        lastServerIndexPlus = config.SERVERS_B + 2 + config.SERVERS_P
        processedJobs = stats.processedJobs[1]
    
    for s in range(firstServerIndex, lastServerIndexPlus):
        d = dict()
        #d['server'] = s
        d['utilization'] = stats.sum[s].service / time.current
        d['service'] = stats.sum[s].service / stats.sum[s].served
        d['share'] = stats.sum[s].served / processedJobs

        ext_dict[s] = d

    return ext_dict


class SamplingEvent:

    avgInterarrivals = None
    avgWaits = None
    avgNumNodes = None
    avgDelays = None
    avgNumQueues = None
    avgServersStats = None

    def __init__(self, stats:Statistics, time:Time):
                
        self.avgInterarrivals = [computeAvgInterarrivals(stats), computeAvgInterarrivals(stats,True) ]
        self.avgWaits = [computeAvgWait(stats), computeAvgWait(stats, True)]
        self.avgNumNodes = [computeAvgNumNode(stats, time), computeAvgNumNode(stats, time, True)]
        self.avgDelays = [computeAvgDelay(stats), computeAvgDelay(stats, True)]
        self.avgNumQueues = [computeAvgNumQueue(stats, time), computeAvgNumQueue(stats, time, True)]
        self.avgServersStats = [computeAvgServerStats(stats, time), computeAvgServerStats(stats, time, True)] 
        

    

    