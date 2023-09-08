
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
    gaussianFactor = 1
    if config.USE_GAUSSIAN_FACTOR:
        gaussianFactor = gaussianWeighter.gaussianWeighterFactorB(time.current, time.timeSlot) 
    b_time = GetArrivalB(1/m) / gaussianFactor
    

    stats.updateArrivalB(dayArrivals[0], b_time)
    # stats.events[0].t is updated to the new arrival time
    dayArrivals[0] = stats.events[0].t
    
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

    l = getCorrectLambdaP(time)
    gaussianFactor = 1
    if config.USE_GAUSSIAN_FACTOR:
        gaussianFactor = gaussianWeighter.gaussianFactorP(time.current)    

    p_time = GetArrivalP(1/l) / gaussianFactor

    dayArrivals[1] += p_time

    # schedule next arrival
    stats.updateArrivalP(dayArrivals[1])

    if (stats.numbers[1] <= config.SERVERS_P):
        service  = GetServiceP()
        s = FindOneP(stats.events)     
        if (s >= 0):
            stats.sum[s].service += service
            stats.sum[s].served += 1
            stats.events[s].t = time.current + service
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

def setInitialState(stats:Statistics, t:Time):
    # select time in which sampling interarrival events. the interarrival will be an uniform 
    # between 1.5 and 2 minutes (90 sec and 120 sec). 
    global samplingInterarrivalTime
    global dayArrivals
    dayArrivals = [config.START_B, config.START_P]
    
    samplingInterarrivalTime = getSamplingInterarrivalTime()
    stats.setSamplingTime(config.START_B + samplingInterarrivalTime)
    #stats.setSamplingTime(Uniform(20*60, 23*60))

    # set the first B arrival
    m = getCorrectLambdaB(t)
    firstB_ArrivalTime = GetArrivalB(m)
    stats.updateArrivalB(dayArrivals[0], firstB_ArrivalTime)
    dayArrivals[0] += firstB_ArrivalTime

    # schedule the first P arrival only if not in infinite case:
    if not config.INFINITE_H:
        m = getCorrectLambdaP(t)
        firstP_Time = GetArrivalP(m)
        dayArrivals[1] += firstP_Time
        if config.DEBUG:
            print(f'firstP_Time {dayArrivals[1]/60}')
        stats.updateArrivalP(dayArrivals[1])

def loop(stats:Statistics, t:Time, listOfSamplingElementList:list[SamplingList]):
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
    reset = False
    while (True): 
        #initializing sampling
        
        e = NextEvent(stats.events)     # next event index */
        t.next = stats.events[e].t      # next event time  */

        stats.areas[0] += (t.next - t.current) * stats.numbers[0]     # update Bintegral  */
        stats.areas[1] += (t.next - t.current) * stats.numbers[1]     # update Pintegral  */
        
        if config.DEBUG:
            print('STATS')
            print(stats)
            print('TIME')
            print(t)
            print()

        if t.next >= config.SECOND_HALFDAY_OPEN_TIME and\
                t.current < config.SECOND_HALFDAY_OPEN_TIME:
            t.current = config.SECOND_HALFDAY_OPEN_TIME
        diff = t.next - t.current
        t.simulationTimeB += diff
        if t.timeSlot == 4:
            t.simulationTimeP += diff
        

        # advance the clock
        t.current = t.next

        oldSlot = t.timeSlot
        #checking if time slot changed:
        t.changeSlot()
        if config.SPLIT_STATS_ANALYSIS_FOR_8_H and t.next >= config.SECOND_HALFDAY_OPEN_TIME \
                and not reset:
            samplingElementList.makeCorrectVariance(False)
            #samplingElementList.computeConfidenceInterval(config.CONFIDENCE_LEVEL, False)
            samplingElementList = listOfSamplingElementList[1]
            
            t.changeBatchTimeB = config.SLOTSTIME[3]
            t.simulationTimeB = 0
            stats.resetStats()
            reset = True

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

            if stats.processedJobs[0] != 0 and not enoughSample:
                currSample = SamplingEvent(paramDic)
                samplingElementList.append(currSample)
            
            #if stats.numbers[1] != 0 and stats.processedJobs[1] != 0 and \
            if (t.timeSlot == 4 and stats.processedJobs[1] != 0) and (config.FINITE_H or \
                        not enoughSample):
                #sample also a P type:
                samplingElementList.append(SamplingEvent(paramDic, True))
            
            if config.DEBUG:
                print('SAMPLING LIST')
                print(samplingElementList)
                print('\n\n')
            if (config.FIND_B_VALUE or config.INFINITE_H):
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
                    
                    stats.resetStats()
                    # all batches done
                    if currBatch_k == config.BATCH_K:
                        return
                    else:
                        # change the times:

                        # restart statistics:
                        t.setBatchTime()  
                        
                        # change the samplingList:
                        samplingElementList = listOfSamplingElementList[currBatch_k]

            
            # stats.events[e].t += samplingInterarrivalTime
            times = []
            for index, ev in enumerate(stats.events):
                if index != e and ev.x == 1:
                    times.append(ev.t)
            stats.events[e].t = min(times) + samplingInterarrivalTime
        
            

        #it's a departure
        else:
            if (e < pArrivalIndex): #B-type
                processDepartureB(stats, t, e)

            else: #P-type
                processDepartureP(stats, t, e)
            

        stats.number = stats.numbers[0] + stats.numbers[1]
       
        # in infinite horizont never stop the arrival process.
        if stats.events[0].x == 0 and stats.number == 0:
            break
    # divide by n each variance before ending
    samplingElementList.makeCorrectVariance(True)

    if not config.SPLIT_STATS_ANALYSIS_FOR_8_H:
        samplingElementList.computeConfidenceInterval(config.CONFIDENCE_LEVEL, True)
    

def batchMeansAnalysis(batches:list[SamplingList], time:Time, fileName:str = None) -> SamplingList:
    # batches is a list of SamplingList
    global stats    
    batchMeans = SamplingList()
    # exponent is to trace 2**exponent. i want to store data for 2 pows
    exponent = 1
    
    processedJobs = [0,0]
    iterations = 1
    if time.timeSlot == 4:
        iterations = 2

    for numSample, sl in enumerate(batches):
        serverStats = deepcopy(sl.serversStats)
        # get statistics for each type B or P:
        for i in range(iterations):
            dic = {}
            # processedJobs are required for computing means from statistics. they are useless here
            # but trace them for next. Later, batchMeans.processeJobs will keep the avg num of node 
            # for each kind
            processedJobs[i] += sl.processedJobs[i]
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
            if fileName and numSample + 1 == pow(2, exponent):
                type = 'B' if i == 0 else 'P'
                outputFileName = f'./output/infinite/{fileName}_slot_{time.timeSlot}_kind_{type}_infinite.csv'
                copyBatch = deepcopy(batchMeans)
                copyBatch.makeCorrectVariance(bool(i))
                copyBatch.computeConfidenceInterval(config.CONFIDENCE_LEVEL, bool(i))
                writeOnFile(f'{outputFileName}', copyBatch, i, addLegend=(exponent==1))
                if i == iterations - 1:
                    exponent += 1

    batchMeans.makeCorrectVariance()
    batchMeans.computeAutocorrelation()

    for i in range(iterations):
        batchMeans.processedJobs[i] = processedJobs[i] // len(batches)
    
    return batchMeans

def writeOnFile(fileName:str, batchMeans:SamplingList, kind:int, addLegend:bool):
    # kind == 0: B-type; kind == 1: P-type
    line = batchMeans.newLine(kind, addLegend)
    #input(
    
    with open(fileName, 'a') as file:
        file.write(line)


def infinite(fileName:str = None):
    
    restart = True
    slotsNum = len(config.SLOTSTIME)
    samplingElementMatrix = None
    # almost one run
    while restart:        
        
        t = Time()
        """ events table:
          index | event     |
          ------------------|
          0 | arrival B     |
          ------------------|
          1 | completion B1 |
          ------------------|
          2 | completion B2 |
          ------------------|
          3 | arrival P     |
          ------------------|
          4 | completion P1 |
          ------------------|
          5 | completion P2 |
          ------------------|
          6 | sampling      |
          ------------------|
        """
        numEvents = config.SERVERS_B + 1 + config.SERVERS_P + 1 + 1
        stats = Statistics(numEvents)
        setInitialState(stats, t)
        
        # matrix of n row, where n is the num of timeslots. Each row is an ensample of BATCH_K batches.
        # each List of the ensample has the relative BATCH_B sample.
        samplingElementMatrix = [[SamplingList() for _ in range(config.BATCH_K)] \
            for _ in range(slotsNum) ] 
    
        # making an ensample of k batches for each slots
        for i in range(slotsNum):
            restart = True
            listOf_K_SamplingElementList = samplingElementMatrix[i]
            loop(stats, t, listOf_K_SamplingElementList)
            # make analisys on lagj:
            batchMeans = batchMeansAnalysis(listOf_K_SamplingElementList, t, fileName)
            
            # evaluateAutocorr returns True if every value of autocorr is < config.THRESHOLD
            if config.FIND_B_VALUE:
                restart = not batchMeans.evaluateAutocorrelation()
            else:
                restart = False

            #input()
            if restart:
                config.BATCH_B[t.timeSlot] *= 2 
                break
            else:
                # update slotTime in deterministic way:
                t.timeSlot += 1
                t.simulationTimeB = 0
                t.simulationTimeP = 0
                if (t.timeSlot == 2):
                    t.timeSlot += 1
                elif t.timeSlot == 4:
                    # initialize p arrival:
                    l = getCorrectLambdaP(t)
                    firstP_Time = GetArrivalP(l)
                    dayArrivals[1] = t.current + firstP_Time
                    stats.updateArrivalP(dayArrivals[1])
                elif t.timeSlot == 6:
                    break

def finite(fileName:str):
    
    runs = []
    numEvents = config.SERVERS_B + 1 + config.SERVERS_P + 1 + 1

    for i in range(config.RUNS):
        t = Time()
        stats = Statistics(numEvents)
        setInitialState(stats, t)

        listOfSamplingList:list[SamplingList] = []
        iterations = 2 if config.SPLIT_STATS_ANALYSIS_FOR_8_H else 1
        for _ in range(iterations):
            listOfSamplingList.append(SamplingList())

        # sampling list has to be put in a list
        loop(stats, t, listOfSamplingList)
        
        samplingList = None
        # merge 2 lists if needed
        if config.SPLIT_STATS_ANALYSIS_FOR_8_H:
            merged = listOfSamplingList[0].merge(listOfSamplingList[1])
            merged.computeConfidenceInterval(config.CONFIDENCE_LEVEL, True)
            samplingList = merged
        else:
            samplingList = listOfSamplingList[0]

        runs.append(samplingList)   
        # for j in range(i+1):
        #     print(f'{j}-th list: \n{runs[j]}\n\n')

        if config.DEBUG:
            paramDic = {'stats': stats, 'time': t}
            lastSampleB = SamplingEvent(paramDic)
            lastSampleP = SamplingEvent(paramDic, True)
            print(lastSampleB)
            print(lastSampleP)
                
    means = runsAnalysis(runs, fileName)
    
    return runs, means


def runsAnalysis(runs:list[SamplingList], fileName:str = None) -> SamplingList:
    # batches is a list of SamplingList
    runsMeans = SamplingList()
    # exponent is to trace 2**exponent. i want to store data for 2 pows
    exponent = 1
    processedJobs = [0,0]
    for numSample, run in enumerate(runs):
        serverStats = deepcopy(run.serversStats)
        # get statistics for each type B or P:
        for i in range(2):
            dic = dict()
            # processedJobs are required for computing means from statistics. they are useless here
            # but trace them for next. Later, batchMeans.processeJobs will keep the avg num of node 
            # for each kind
            processedJobs[i] += run.processedJobs[i]
            dic['processedJobs'] = 0
            dic['avgInterarrivals'] = run.avgInterarrivals[i]['mean']
            dic['avgWaits'] = run.avgWaits[i]['mean']
            dic['avgNumNodes'] = run.avgNumNodes[i]['mean']
            dic['avgDelays'] = run.avgDelays[i]['mean']
            dic['avgNumQueues'] = run.avgNumQueues[i]['mean']
            
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
                d['utilization'] = serverStats[s]['utilization']['mean']
                d['service'] = serverStats[s]['service']['mean']
                d['share'] = serverStats[s]['share']['mean']

                ext_dict[s] = d

            #print(dic['avgWaits'])
            dic['avgServersStats'] = ext_dict
            
            # make a sampling event with the batch statistics
            sample = SamplingEvent(dic, bool(i))

            # append the sample to automatically compute avg variance and lag j
            runsMeans.append(sample)  

        # write on file when both B and P type are sampled, each 2^i iteration, for each kind:
        
        if fileName and numSample + 1 == pow(2, exponent):
            for i in range(2):
                kind = 'B' if i == 0 else 'P'
                outputFileName = f'./output/finite/{fileName}_finite_{kind}.csv'
                copyRun = deepcopy(runsMeans)
                copyRun.makeCorrectVariance(bool(i))
                copyRun.computeConfidenceInterval(config.CONFIDENCE_LEVEL, bool(i))
                writeOnFile(f'{outputFileName}', copyRun, i, addLegend=(exponent==1))
            exponent += 1

    runsMeans.makeCorrectVariance(True)
    runsMeans.computeConfidenceInterval(config.CONFIDENCE_LEVEL,True)
    # setting up the avg number of job for each kind:
    for i in range(2):
        runsMeans.processedJobs[i] = processedJobs[i] // len(runs)
    return runsMeans


""" def storeToFile():
    
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
            
            transientOut.write(line) """



############################Main Program###################################
if __name__ == '__main__':
    global dayArrivals
    global gaussianWeighter

    parser = ArgParser()
    parser.parse()
    outputFile = parser.getOutputFileName()
    if outputFile:
        outputFile = outputFile.strip('.csv')

    dayArrivals = [config.START_B, config.START_P]
    gaussianWeighter = GaussianWeighter()

    seed = config.SEED
    plantSeeds(seed)
     
    """ events table:
      index | event     |
      ------------------|
      0 | arrival B     |
      ------------------|
      1 | completion B1 |
      ------------------|
      2 | completion B2 |
      ------------------|
      3 | arrival P     |
      ------------------|
      4 | completion P1 |
      ------------------|
      5 | completion P2 |
      ------------------|
      6 | sampling      |
      ------------------|
    """


    if (config.FIND_B_VALUE or config.INFINITE_H):
        infinite(outputFile)   

    elif config.FINITE_H:
        runs, means = finite(outputFile)
        print(means)

    else: 
        # single run. not so interesting
        t = Time()
        numEvents = config.SERVERS_B + 1 + config.SERVERS_P + 1 + 1
        stats = Statistics(numEvents)
        setInitialState(stats, t)
        listOfSamplingList = []
        iterations = 2 if config.SPLIT_STATS_ANALYSIS_FOR_8_H else 1
        for i in range(iterations):
            listOfSamplingList.append(SamplingList())

        # sampling list has to be put in a list
        loop(stats, t, listOfSamplingList)
        
        # printing half day lists or single list if not SPLIT_STATS_ANALYSIS_FOR_8_H
        for index,samplingList in enumerate(listOfSamplingList):
            if config.SPLIT_STATS_ANALYSIS_FOR_8_H: 
                if index == 0:
                    print('FIRST 8 HOURS:')
                else:
                    print('SECOND 8 HOURS:')

            print(samplingList)

        # global analysis
        if config.SPLIT_STATS_ANALYSIS_FOR_8_H:
            print('\n\nGLOBALS:')
            merged = listOfSamplingList[0].merge(listOfSamplingList[1])
            merged.computeConfidenceInterval(config.CONFIDENCE_LEVEL, True)
            print(merged)

    parser.storePersonalConfig()

    