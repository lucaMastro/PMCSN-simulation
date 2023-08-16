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
    dict_list = []
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
        d['server'] = s
        d['utilization'] = stats.sum[s].service / time.current
        d['avg_service'] = stats.sum[s].service / stats.sum[s].served
        d['share'] = stats.sum[s].served / processedJobs

        dict_list.append(d)

    return dict_list


class SamplingEvent:

    avgInterarrivals = None
    avgWaits = None
    avgNumNodes = None
    avgDelays = None
    avgNumQueues = None
    serversStats = None

    def __init__(self, stats:Statistics, time:Time):
                
        self.avgInterarrivals = [computeAvgInterarrivals(stats), computeAvgInterarrivals(stats,True) ]
        self.avgWait = [computeAvgWait(stats), computeAvgWait(stats, True)]
        self.avgNumNode = [computeAvgNumNode(stats, time), computeAvgNumNode(stats, time, True)]
        self.avgDelay = [computeAvgDelay(stats), computeAvgDelay(stats, True)]
        self.avgNumQueue = [computeAvgNumQueue(stats, time), computeAvgNumQueue(stats, time, True)]
        self.serverStats = [computeAvgServerStats(stats, time), computeAvgServerStats(stats, time)] 
        

    

    