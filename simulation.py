
from support.functions import *
from support.rngs import plantSeeds
from support.SamplingEvent import SamplingEvent
from support.Time import Time
from support.Statistics import Statistics
from support.SamplingList import SamplingList
import support.Config as config


""" def evaluation(stats, listOfSample):
    l = len(listOfSample)
    titles = ["BAR:\n", "PIZZERIA:\n"]
    indexes = None

    if l == 1:
        # STEADY ANALISYS
        indexes = listOfSample[0].indexes 
        index = indexes[0] + indexes[1]
        print("\nfor {0:1d} jobs the service node statistics are:\n".format(index))
        stop = config.STOP
    else:
        # TRANSIENT ANALISYS
        print("\n\nTransient analisys:")

        # computing means
        #
        # computing average index 
        numSample = len(samplingElementList)
        
        indexes = [0, 0] 
        for i in range(numSample):
            indexes[0] += samplingElementList[i].indexes[0] 
            indexes[1] += samplingElementList[i].indexes[1]
        indexes = [int(i / numSample) for i in indexes]
        index = indexes[0] + indexes[1]

        print("\nfor {0:1d} jobs the service node statistics are:\n".format(index))

        # ?????????????
        # computing average number of elapsed days 
        tmp = 0
        for i in range(numSample):
            tmp += samplingElementList[i].time.day
        stop = int(tmp / numSample)

        # ?????????????? quando faccio il sampling l'ultimo arrivo potrebbe non essere 
        # avvenuto: infatti il sampling avviene in un momento random dell'ultima fascia 
        # oraria, e non è detto che poi non ce ne siano altri
        # computing average lastArrival
        tmpB = 0
        tmpP = 0
        for i in range(numSample):
            tmpB += samplingElementList[i].lastArrivals[0] 
            tmpP += samplingElementList[i].lastArrivals[1]
        lastArrivalsTime = [tmpB/numSample, tmpP/numSample]

        # computing average areas
        tmpB = 0
        tmpP = 0
        for i in range(numSample):
            tmpB += samplingElementList[i].areas[0]
            tmpP += samplingElementList[i].areas[1]
        areas = [tmpB / numSample, tmpP / numSample]

        # computing mean served and service time for each server:
        # there is a AccumSum obj for each event in eventList. the last one is the
        # sampling element: that's why it's excluded. Also exclude the B Arrival index, that
        # is 0
        for s in range(1, len(sum) - 1): 
            if s == pArrivalIndex: #the arrivalP event, then skip
                continue
            service = 0
            served = 0
            for i in range(numSample):
                service += samplingElementList[i].sum[s].service
                served += samplingElementList[i].sum[s].served
            sum[s].served = served / numSample 
            sum[s].service = service / numSample

    serviceTimes = [19 * 60 * stop, 2 * 60 * stop]
    tmp = lastArrivalsTime[0] - config.START_B
    tmp += 19 * 60 * (stop - 1) 
    lastArrivalsTime[0] = tmp

    tmp = lastArrivalsTime[1] - config.START_P
    tmp += 2 * 60 * (stop - 1)
    lastArrivalsTime[1] = tmp
    for i in range(2):
        print(titles[i])
        print("  avg interarrivals .. = {0:6.2f}".format(lastArrivalsTime[i] /
            indexes[i])) 
        
        print("  avg wait ........... = {0:6.2f}".format(areas[i] / indexes[i]))
        # avg # in node is the mean population in the node on the "up-time"
        print("  avg # in node ...... = {0:6.2f}".format(areas[i] / serviceTimes[i]))

        if (i == 0):
            startingPoint = 1
            endPoint = config.SERVERS_B + 1
        else:
            startingPoint = config.SERVERS_B + 1 
            endPoint = len(events) - 1          #excluding sampling 
        for s in range(startingPoint, endPoint):  # adjust area to calculate */ 
            if (s != pArrivalIndex):
                areas[i] -= sum[s].service              # averages for the queue   */    

        print("  avg delay .......... = {0:6.2f}".format(areas[i] / indexes[i]))
        print("  avg # in queue ..... = {0:6.2f}".format(areas[i] / serviceTimes[i]))
        print("\nthe server statistics are:\n")
        print("    server     utilization     avg service        share\n")

        for s in range(startingPoint, endPoint):  
            if (s != pArrivalIndex):
              print("{0:8d} {1:14.3f} {2:15.2f} {3:15.3f}".format(s, sum[s].service
                  / serviceTimes[i], sum[s].service / sum[s].served,float(sum[s].served)
                  / indexes[i]))
        if (i == 0):
            print("\n\n")

    # revenue analisys
    monthsNum = int(stop / 30) # number of months
    # if ( stop % 30 != 0):
    #    monthsNum += 1
    rentCost = monthsNum * config.RENT 

    peopleCost= stop * config.COSTS[0] * config.SERVERS_B + stop * config.COSTS[1] * config.SERVERS_P / 2 

    # computing total served requests for each type
    total_B_services = 0
    for s in range(1, config.SERVERS_B + 1):
        total_B_services += sum[s].served

    total_P_services = 0
    for s in range(config.SERVERS_B + 2, len(events) - 1):     #excludin sampling event
        total_P_services += sum[s].served

    # grass revenue 
    revenue = total_B_services * config.REVENUES[0] + total_P_services * config.REVENUES[1]

    # each request costs to restaurant half of its selling cost
    # meaning that if request B costs 3€, it has been bought at 1.50€
    # by restaurant
    materialCost = revenue / 2

    # computing iva at 22%
    ivaCost = revenue * config.IVA

    #computing bill costs
    billCosts = monthsNum * config.BILL_COSTS 

    print("\n\nREVENUE ({0} days):\n".format(stop))
    print("  Gross revenue...... = {0:.2f} €".format(revenue))
    print("  Personal cost...... = {0:.2f} €".format(peopleCost))
    revenue -= peopleCost
    print("  Material cost...... = {0:.2f} €".format(materialCost))
    revenue -= materialCost 
    print("  Rent costs......... = {0:.2f} €".format(rentCost))
    revenue -= rentCost
    print("  Iva costs.......... = {0:.2f} €".format(ivaCost))
    revenue -= ivaCost
    print("  Bill costs......... = {0:.2f} €".format(billCosts))
    revenue -= billCosts 
    print("  Revenue for year... = {0:.2f} €".format(revenue))
    print("  Revenue for month.. = {0:.2f} €".format(revenue / monthsNum))
     """



def processArrivalB(stats:Statistics, time:Time):
    global dayArrivals
    stats.numbers[0] += 1 
    stats.number += 1
    
    stats.lastArrivalsTime[0] = stats.events[0].t 

    m = getCorrectInterarrivalB(time)
    b_time = GetArrivalB(m)

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
    #print("P-ARRIVAL")
    pArrivalIndex = config.SERVERS_B + 1
    stats.numbers[1] += 1
    stats.number += 1

    stats.lastArrivalsTime[1] = stats.events[pArrivalIndex].t 

    m = getCorrectInterarrivalP(time.dayOfWeek)
    p_time = GetArrivalP(m)

    dayArrivals[1] += p_time

    # schedule next arrival
    stats.updateArrivalP(dayArrivals[1])

    if (stats.numbers[1] <= config.SERVERS_P):
        service  = GetServiceP()
        s = FindOneP(stats.events)
        global p_servers_usage 
        p_servers_usage[str(s)] += 1
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


############################Main Program###################################
if __name__ == '__main__':
    global dayArrivals
    global p_servers_usage
    p_servers_usage = {'4': 0, '5': 0}

    t = Time()
    dayArrivals = [config.START_B, config.START_P]

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
    pArrivalIndex = config.SERVERS_B + 1

    # samplingElementList = []
    samplingElementList = SamplingList()
    # initializedP = False #this variable is used to "open door" to P-arrivals
    stats = Statistics(numEvents)

    plantSeeds(0)

    # select time in which sampling events will be scheduled: it will be scheduled
    # every day at same time
    samplingTime = getSamplingTime()
    stats.setSamplingTime(samplingTime)

    # set the first B arrival
    m = getCorrectInterarrivalB(t)
    firstB_ArrivalTime = GetArrivalB(m)
    stats.updateArrivalB(dayArrivals[0], firstB_ArrivalTime)
    dayArrivals[0] += firstB_ArrivalTime

    # schedule the first P arrival
    m = getCorrectInterarrivalP(t.dayOfWeek)
    firstP_Time = GetArrivalP(m)
    dayArrivals[1] += firstP_Time
    stats.updateArrivalP(dayArrivals[1])
    
    # t.day < config.STOP and not <= because if you want to perform 365 days starting from
    # 0 (t.day is initialized to 0), you have to terminate when the 364th day ends
    
    if config.DEBUG:
        print('START')
    while (t.day < config.STOP) or (stats.number != 0):
        #initializing sampling
        
        e = NextEvent(stats.events)     # next event index */
        t.next = stats.events[e].t      # next event time  */

        if config.DEBUG:
            print(f'day num: {t.day}')
            print(f'curr time: {t.current} == {t.current / 60}')
            stats.printEvents()
            print(f'number: {stats.number}')
            print(f'numbers[0]: {stats.numbers[0]}')
            print(f'numbers[1]: {stats.numbers[1]}')
            print(f'weekday: {t.dayOfWeek}')
            print(f'event index: {e}')
            print()

        stats.areas[0] += (t.next - t.current) * stats.numbers[0]     # update Bintegral  */
        stats.areas[1] += (t.next - t.current) * stats.numbers[1]     # update Pintegral  */
        
        # advance the clock
        t.current = t.next
        #checking if time slot changed:
        t.changeSlot()

        if (e == 0): 
             # process a B-arrival 
            processArrivalB(stats, t)
                
        elif (e == pArrivalIndex): # process a P-arrival*/
            processArrivalP(stats, t)

        elif (e == len(stats.events) - 1):
            # it's a sampling event
            currSample = SamplingEvent(stats, t)
            samplingElementList.append(currSample)
            stats.events[e].x = 0

        #it's a departure
        else:
            if (e < pArrivalIndex): #B-type
                processDepartureB(stats, t, e)

            else: #P-type
                processDepartureP(stats, t, e)
            

        stats.number = stats.numbers[0] + stats.numbers[1]
        if (stats.events[0].x == 0) and (stats.number == 0):
            
            #it means that a day is over: re-initialize all variables and let days advance:
            dayArrivals = [config.START_B, config.START_P]
            
            t.newDay()
            m = getCorrectInterarrivalB(t)
            newDayFirstArrivalB = GetArrivalB(m)
            dayArrivals[0] += newDayFirstArrivalB

            m = getCorrectInterarrivalP(t.dayOfWeek)
            newDayFirstArrivalP = GetArrivalP(m)
            dayArrivals[1] += newDayFirstArrivalP

            stats.newDay(dayArrivals)
    

    lastSample = SamplingEvent(stats, t)
    # evaluation([lastSample])
    # evaluation(samplingElementList)

    if config.DEBUG:
        print('WHILE ENDED')
        print(stats.number)
        print(t.day)
        print(p_servers_usage)

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