from support.Time import Time
from support.Statistics import Statistics

from configurations.Config import config

def computeAvgInterarrivals(stats:Statistics, kindP=False):
    interarrivalWindow = None
    processedJobs = None
    if not kindP:
        interarrivalWindow = stats.lastArrivalsTime[0] - config.START_B
        processedJobs = stats.processedJobs[0] 
    else:
        interarrivalWindow = stats.lastArrivalsTime[1] - config.START_P
        processedJobs = stats.processedJobs[1]
    return interarrivalWindow / processedJobs

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

    # 0 for B; 1 for P
    type = None

    avgInterarrivals = None
    avgWaits = None
    avgNumNodes = None
    avgDelays = None
    avgNumQueues = None
    avgServersStats = None
    processedJobs = None

    def __init__(self, stats:Statistics, time:Time, kindP=False):
        # if config.DEBUG:
        #     print('\n\n\n\n')
        #     print(stats)
        #     print(time)
        #     print('\n\n\n\n')
        
        self.type = 1 if kindP else 0
            
        self.processedJobs = stats.processedJobs[self.type]
        self.avgInterarrivals = computeAvgInterarrivals(stats, kindP)
        self.avgWaits = computeAvgWait(stats, kindP)
        self.avgNumNodes = computeAvgNumNode(stats, time, kindP)
        self.avgDelays = computeAvgDelay(stats, kindP)
        self.avgNumQueues = computeAvgNumQueue(stats, time, kindP)
        self.avgServersStats = computeAvgServerStats(stats, time, kindP)
        

    def __str__(self) -> str:
        my_string = ''
        titles = ["BAR:\n", "PIZZERIA:\n"]
        
        
        my_string += titles[self.type]
        my_string += "  avg interarrivals .. = {0:6.2f}\n".format(self.avgInterarrivals)
        
        my_string += "  avg wait ........... = {0:6.2f}\n".format(self.avgWaits)
        
        my_string += "  avg # in node ...... = {0:6.2f}\n".format(self.avgNumNodes)

        startingPoint = None
        endingPoint = None
        if (self.type == 0):
            startingPoint = 1
            endingPoint = config.SERVERS_B + 1
        else:
            startingPoint = config.SERVERS_B + 2 
            endingPoint = config.SERVERS_B + 2 + config.SERVERS_P
        
        my_string += "  avg delay .......... = {0:6.2f}\n".format(self.avgDelays)
        my_string += "  avg # in queue ..... = {0:6.2f}\n".format(self.avgNumQueues)
        my_string += "\nthe server statistics are:\n"
        my_string += "    server     utilization     avg service        share\n"

        # if config.DEBUG:
        #     print(f"SERVER: {self.avgServersStats}")

        for s in range(startingPoint, endingPoint):  
            
            my_string += "{0:8d} {1:14.3f} {2:15.2f} {3:15.3f}\n".format(s, self.avgServersStats[s]['utilization'], 
                self.avgServersStats[s]['service'], 
                self.avgServersStats[s]['share'])
        my_string += '\n'
        return my_string

    

    