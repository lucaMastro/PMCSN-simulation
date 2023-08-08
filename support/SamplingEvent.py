from support.Time import Time
from support.Statistics import Statistics

class SamplingEvent:
    processedJobs = None
    lastArrivals = None
    areas = None
    sum = None 
    time = None 
    numberB = None
    numberP = None 


    def __init__(self, stats:Statistics, time:Time):
        newAreas = [i for i in stats.areas]
        self.areas = newAreas

        newProcessedJobs = [i for i in stats.processedJobs]
        self.processedJobs = newProcessedJobs

        newArrivals = [i for i in stats.lastArrivalsTime]
        self.lastArrivals = newArrivals

        newSum = []
        for s in range(len(stats.sum)):
            newSum.append(stats.sum[s].copy())
        self.sum = newSum

        self.time = time.copy()

        self.numberB = stats.numbers[0]
        self.numberP = stats.numbers[1]
