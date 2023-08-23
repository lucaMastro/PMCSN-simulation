
from support.functions import *
from support.rngs import plantSeeds
from support.SamplingEvent import SamplingEvent
from support.Time import Time
from support.Statistics import Statistics
from support.SamplingList import SamplingList
from support.GaussianWeighter import GaussianWeighter
from support.ArgParser import ArgParser
from copy import deepcopy

from configurations.Config import config

def processArrivalB(stats:Statistics, time:Time):
    global dayArrivals
    global gaussianWeighter
    stats.numbers[0] += 1 
    stats.number += 1
    
    stats.lastArrivalsTime[0] = stats.events[0].t 

    m = getCorrectLambdaB(time)
    gaussianFactor = gaussianWeighter.gaussianWeighterFactorB(time.current, time.timeSlot)
    if not config.USE_GAUSSIAN_FACTOR:
        gaussianFactor = 1
    b_time = GetArrivalB(1/m) / gaussianFactor

    stats.updateArrivalB(dayArrivals[0], b_time)
    dayArrivals[0] += b_time
    
    if (stats.numbers[0] <= config.SERVERS_B):
        # there is an idle B-server
        service = GetServiceB()
        s = FindOneB(stats.events)
        if (s >= 0):
            stats.sum[s].service += service
            stats.sum[s].served += 1
            # the s server will be idle at t.current + service
            stats.events[s].t = time.current + service
            stats.events[s].x = 1


def processArrivalP(stats:Statistics, time:Time):
    global dayArrivals
    global gaussianWeighter
    #print("P-ARRIVAL")
    pArrivalIndex = config.SERVERS_B + 1
    stats.numbers[1] += 1
    stats.number += 1

    stats.lastArrivalsTime[1] = stats.events[pArrivalIndex].t 

    m = getCorrectLambdaP(time)
    gaussianFactor = gaussianWeighter.gaussianFactorP(time.current)
    if not config.USE_GAUSSIAN_FACTOR:
        gaussianFactor = 1
    p_time = GetArrivalP(1/m) / gaussianFactor

    dayArrivals[1] += p_time

    # schedule next arrival
    stats.updateArrivalP(dayArrivals[1])

    if (stats.numbers[1] <= config.SERVERS_P):
        service  = GetServiceP()
        s = FindOneP(stats.events)
    
        
        if (s >= 0):
            stats.sum[s].service += service
            stats.sum[s].served += 1
            stats.events[s].t = t.current + service
            stats.events[s].x = 1

def processDepartureB(stats:Statistics, time:Time, serverIndex:int):
    stats.processedJobs[0] += 1
    stats.numbers[0] -= 1
    stats.number -= 1
    
    if (stats.numbers[0] >= config.SERVERS_B):
        service = GetServiceB()
        stats.sum[serverIndex].service += service
        stats.sum[serverIndex].served += 1
        stats.events[serverIndex].t = time.current + service
    else:
        stats.events[serverIndex].x = 0

def processDepartureP(stats:Statistics, time:Time, serverIndex:int):
    # print("P-DEPARTURE")
    stats.processedJobs[1] += 1
    stats.numbers[1] -= 1
    stats.number -= 1
    
    if (stats.numbers[1] >= config.SERVERS_P):
        service = GetServiceP()
        stats.sum[serverIndex].service += service
        stats.sum[serverIndex].served += 1
        stats.events[serverIndex].t = time.current + service
    else:
        stats.events[serverIndex].x = 0


def setInitialState(stats:Statistics):
    # select time in which sampling interarrival events. the interarrival will be an uniform 
    # between 1.5 and 2 minutes (90 sec and 120 sec). 
    global samplingInterarrivalTime
    samplingInterarrivalTime = getSamplingInterarrivalTime()
    stats.setSamplingTime(config.START_B + samplingInterarrivalTime)
    #stats.setSamplingTime(Uniform(20*60, 23*60))

    # set the first B arrival
    m = getCorrectLambdaB(t)
    firstB_ArrivalTime = GetArrivalB(m)
    stats.updateArrivalB(dayArrivals[0], firstB_ArrivalTime)
    dayArrivals[0] += firstB_ArrivalTime

    # schedule the first P arrival
    m = getCorrectLambdaP(t)
    firstP_Time = GetArrivalP(m)
    dayArrivals[1] += firstP_Time
    stats.updateArrivalP(dayArrivals[1])



def loop(stats:Statistics, t:Time, listOfSamplingElementList:list):
    global dayArrivals
    global samplingInterarrivalTime

    pArrivalIndex = config.SERVERS_B + 1

    # infinite horizont param:
    enoughSample = False
    currBatch_k = 0
    batch_b = config.BATCH_B[currBatch_k]
    
    # always start from timeslot 0. This will change only for infinite h. simulation
    # when a batch is full
    samplingElementList = listOfSamplingElementList[0]

    while (t.day < config.STOP): 
        #initializing sampling
        
        e = NextEvent(stats.events)     # next event index */
        t.next = stats.events[e].t      # next event time  */

        stats.areas[0] += (t.next - t.current) * stats.numbers[0]     # update Bintegral  */
        stats.areas[1] += (t.next - t.current) * stats.numbers[1]     # update Pintegral  */
        
        # advance the clock
        t.current = t.next
        #checking if time slot changed:
        t.changeSlot()

        if config.DEBUG:
            print('STATS')
            print(stats)
            print('TIME')
            print(t)
            print()

        if (e == 0): 
             # process a B-arrival 
            processArrivalB(stats, t)
                
        elif (e == pArrivalIndex): # process a P-arrival*/
            processArrivalP(stats, t)

        elif (e == len(stats.events) - 1):
            # it's a sampling event
            # sample only if statistics are ready and we need more sample in infinite horizont case. 
            # BATCH_B is the number of sample required
            paramDic = {'stats': stats, 'time': t}

            if stats.processedJobs[0] != 0 and \
                (config.INFINITE_H or config.FIND_B_VALUE) and \
                    not enoughSample:
                currSample = SamplingEvent(paramDic)
                
                samplingElementList.append(currSample)
                enoughSample = False
            
            #if stats.numbers[1] != 0 and stats.processedJobs[1] != 0 and \
            if t.timeSlot == 4 and stats.processedJobs[1] != 0 and \
                    (config.INFINITE_H or config.FIND_B_VALUE) and \
                        not enoughSample:
                #sample also a P type:
                samplingElementList.append(SamplingEvent(paramDic, True))
                
            # check if enough samples:
            enoughSampleB = batch_b <= samplingElementList.numSampleB 
            enoughSampleP = batch_b <= samplingElementList.numSampleP 
            enoughSample = enoughSampleB
            if t.timeSlot == 4:
                enoughSample = enoughSampleB and enoughSampleP 
    
            if enoughSample:
                # update the variances and correlations:
                samplingElementList.makeCorrectVariance(alsoP=(t.timeSlot == 4))
            
                # update slotTime in deterministic way:
                currBatch_k += 1   
                
                # all batches done
                if currBatch_k == config.BATCH_K:
                    return
                else:
                    # restart statistics:
                    stats.resetStats()
                    # change the samplingList:
                    samplingElementList = listOfSamplingElementList[currBatch_k]

            else: 
                stats.events[e].t += samplingInterarrivalTime
            

        #it's a departure
        else:
            if (e < pArrivalIndex): #B-type
                processDepartureB(stats, t, e)

            else: #P-type
                processDepartureP(stats, t, e)
            

        stats.number = stats.numbers[0] + stats.numbers[1]
        # in infinite horizont never stop the arrival process.
        if stats.events[0].x == 0 and stats.number == 0:
            
            #it means that a day is over: re-initialize all variables and let days advance:
            dayArrivals = [config.START_B, config.START_P]
            
            t.newDay()
            m = getCorrectLambdaB(t)
            newDayFirstArrivalB = GetArrivalB(m)
            dayArrivals[0] += newDayFirstArrivalB

            m = getCorrectLambdaP(t)
            newDayFirstArrivalP = GetArrivalP(m)
            dayArrivals[1] += newDayFirstArrivalP

            stats.newDay(dayArrivals)
            
    # divide by n each variance before ending
    samplingElementList.makeCorrectVarianceAndAutocorr()


def storeBatch_B(slotTime:int, batchB:int):
    with open('./output/BatchB.csv', 'a') as f:
        f.write(f'{slotTime}, {batchB}')


def batchMeansAnalysis(batches:list) -> SamplingList:
    # batches is a list of SamplingList
    global stats

    batchMeans = SamplingList()
    for sl in batches:
        serverStats = deepcopy(sl.serversStats)
        # get statistics for each type B or P:
        for i in range(2):
            dic = {}
            # processedJobs are required for computing means from statistics. they are useless here
            dic['processedJobs'] = 0
            dic['avgInterarrivals'] = sl.avgInterarrivals[i]['mean']
            dic['avgWaits'] = sl.avgWaits[i]['mean']
            dic['avgNumNodes'] = sl.avgNumNodes[i]['mean']
            dic['avgDelays'] = sl.avgDelays[i]['mean']
            dic['avgNumQueues'] = sl.avgNumQueues[i]['mean']
            
            ext_dict = dict()
            firstServerIndex = None
            # the following keep lastServerIndex + 1. It's the right extreme of for cycle
            lastServerIndexPlus = None
            if not bool(i):
                firstServerIndex = 1
                lastServerIndexPlus = config.SERVERS_B + 1
            else:
                firstServerIndex = config.SERVERS_B + 2
                lastServerIndexPlus = config.SERVERS_B + 2 + config.SERVERS_P
            for s in range(firstServerIndex, lastServerIndexPlus):
                d = dict()
                #d['server'] = s
                d['utilization'] = serverStats[s]['utilization']['mean']
                d['service'] = serverStats[s]['service']['mean']
                d['share'] = serverStats[s]['share']['mean']

                ext_dict[s] = d

            dic['avgServersStats'] = ext_dict
        
            
            # make a sampling event with the batch statistics
            sample = SamplingEvent(dic, bool(i))

            # append the sample to automatically compute avg variance and lag j
            batchMeans.append(sample)  

    batchMeans.makeCorrectVariance()
    batchMeans.computeAutocorrelation()
    
    #input()
    return batchMeans


############################Main Program###################################
if __name__ == '__main__':
    global dayArrivals
    global gaussianWeighter

    
    parser = ArgParser()
    parser.parse()
    stats = None
    t = None
    restart = True
    slotsNum = len(config.SLOTSTIME)
    # almost one run
    while restart:        
        dayArrivals = [config.START_B, config.START_P]
        gaussianWeighter = GaussianWeighter()
        t = Time()

        # events table:
        #   index | event     |
        #   ------------------|
        #   0 | arrival B     |
        #   ------------------|
        #   1 | completion B1 |
        #   ------------------|
        #   2 | completion B2 |
        #   ------------------|
        #   3 | arrival P     |
        #   ------------------|
        #   4 | completion P1 |
        #   ------------------|
        #   5 | completion P2 |
        #   ------------------|
        #   6 | sampling      |
        #   ------------------|
        #
        numEvents = config.SERVERS_B + 1 + config.SERVERS_P + 1 + 1
        stats = Statistics(numEvents)

        # matrix of n row, where n is the num of timeslots. Each row is an ensample of BATCH_K batches.
        # each List of the ensample has the relative BATCH_B sample.
        samplingElementMatrix = [[SamplingList() for _ in range(config.BATCH_K)] \
            for _ in range(slotsNum) ] 
        #samplingElementList = SamplingList()
        
        seed = config.SEED
        plantSeeds(seed)
        setInitialState(stats)

        # making an ensample of k batches for each slots
        for i in range(slotsNum):
            listOf_K_SamplingElementList = samplingElementMatrix[i]
            loop(stats, t, listOf_K_SamplingElementList)
            # make analisys on lagj:
            batchMeans = batchMeansAnalysis(listOf_K_SamplingElementList)
            
            # evaluateAutocorr returns True if every value of autocorr is < config.THRESHOLD
            restart = not batchMeans.evaluateAutocorrelation()

            #input()
            if restart:
                config.BATCH_B[t.timeSlot] *= 2 
                break
            else:
                # update slotTime in deterministic way:
                t.timeSlot += 1
                if (t.timeSlot == 2):
                    t.timeSlot += 1
                elif t.timeSlot == 6:
                    break


    """
    # create a csv for analisys 
    firstLine = "day,# job completati, # job B completati, # job P completati," + \
            "#job B nel nodo, # job P nel nodo, # coda B, #coda P," + \
            "last arrival B [H], last arrival" + \
            " P [H], area B, area P, revenue B, revenue P, revenue, costs, " + \
            "daily revenue, incremental grass revenue, incremental revenue, incremental costs\n"

    fileName = 'output/transient_m={}.csv'.format(config.SERVERS_B)
    with open(fileName, 'w') as transientOut:
        transientOut.write(firstLine)

        precIndexB = 0
        precIndexP = 0
        for i in range(len(samplingElementList)):
            elem = samplingElementList[i]
            day = elem.time.day
            
            queueB = elem.numberB - config.SERVERS_B 
            if (queueB < 0):
                queueB = 0
            queueP = elem.numberP - config.SERVERS_P 
            if (queueP < 0):
                queueP = 0

            tmpB = elem.indexes[0] 
            tmpP = elem.indexes[1] 
            incRevenue = tmpB * config.REVENUES[0] 
            incRevenue += tmpP * config.REVENUES[1]

            jobB = tmpB - precIndexB 
            jobP = tmpP - precIndexP 
            precIndexB = tmpB
            precIndexP = tmpP

            totalJob = jobB + jobP 
            lastArrB = elem.lastArrivals[0]
            lastArrP = elem.lastArrivals[1]
            areaB = elem.areas[0]
            areaP = elem.areas[1]
            
            stop = elem.time.day + 1

            #daily people cost
            peopleCost = config.COSTS[0] * config.SERVERS_B + \
                    config.COSTS[1] * config.SERVERS_P / 2 
            
            incCosts = peopleCost * stop 

            # grass revenue 
            revenueB = jobB * config.REVENUES[0] 
            revenueP = jobP * config.REVENUES[1]
            revenue = revenueB + revenueP 

            # each request costs to restaurant half of its selling cost
            # meaning that if request B costs 3€, it has been bought at 1.50€
            # by restaurant
            materialCost = revenue / 2
            incCosts += incRevenue / 2

            # computing iva at 22%
            ivaCost = revenue * config.IVA / 100
            incCosts += incRevenue * config.IVA / 100

            totCost = peopleCost + materialCost + ivaCost 
            # rent and bills costs are payed at the end of month. to seplify, they
            # are split out during the days 
            totCost += (config.RENT + config.BILL_COSTS) / 30
            incCosts += (config.RENT + config.BILL_COSTS) * stop / 30

            line = \
            '{0},{1},{2},{3},{4},{5},{6},{7},{8:.2f},{9:.2f},{10:.2f},{11:.2f},'. \
            format(day + 1, totalJob, jobB, jobP, elem.numberB,  
                    elem.numberP, queueB, queueP, \
                    lastArrB / 60, lastArrP / 60, areaB,\
                    areaP) 
            line += '{0:.2f},{1:.2f},{2:.2f},{3:.2f},{4:.2f},{5:.2f},{6:.2f},{7:.2f}\n'.format(revenueB,\
                    revenueP, revenue, totCost, revenue - totCost, incRevenue,
    incRevenue - incCosts,incCosts)
            
            transientOut.write(line)

 """