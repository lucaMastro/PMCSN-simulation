from rngs import plantSeeds, random, selectStream
from math import log
import copy

import constants as c



def Uniform(a,b):  
# --------------------------------------------
# * generate a Uniform random variate, use a < b 
# * --------------------------------------------
# */
  return (a + (b - a) * random())  

def getSamplingTime():
    selectStream(4) 
    # choosing a value between 20 and 22: otherwise P-type variables may not 
    # be sampled
    return (Uniform(c.SLOTSTIME[(len(c.SLOTSTIME) -2)], 
        c.SLOTSTIME[len(c.SLOTSTIME) - 1]))


def Exponential(m):
# ---------------------------------------------------
# * generate an Exponential random variate, use m > 0.0 
# * ---------------------------------------------------
# */
    return (-m * log(1.0 - random()))


def getCorrectInterarrival(isP = False):
#   checking if it's a weekend:
    m = 0
    if (t.dayOfWeek > 4):
        if (isP):
            m = c.WEEKEND_INTERARRIVAL_P
        else:
            m = c.WEEKEND_INTERARRIVAL_B[t.timeSlot]
    else: # week day
        if (isP):
            m = c.WEEK_INTERARRIVAL_P
        else:
            m = c.WEEK_INTERARRIVAL_B[t.timeSlot]
    return m



def GetArrivalB():
# ---------------------------------------------
# * generate the next arrival time, with rate 1/2
# * ---------------------------------------------
# */ 
    global ARRIVAL_TEMPS

    selectStream(0) 
    m = getCorrectInterarrival()
    c.ARRIVAL_TEMPS[0] += Exponential(m)
    return (c.ARRIVAL_TEMPS[0])


def GetArrivalP():
# ---------------------------------------------
# * generate the next arrival time, with rate 1/2
# * ---------------------------------------------
# */ 
    global ARRIVAL_TEMPS

    selectStream(1) 
    m = getCorrectInterarrival(True)
    #print(t.dayOfWeek, t.current, m)
    c.ARRIVAL_TEMPS[1] += Exponential(m)
    return (c.ARRIVAL_TEMPS[1]) 

def GetServiceB():
# --------------------------------------------
# * generate the next service time with rate 1/6
# * --------------------------------------------
# */ 
    selectStream(2)
    #service type B has a rate of 1/2
    return Exponential(2)
  
def GetServiceP():
# --------------------------------------------
# * generate the next service time with rate 1/6
# * --------------------------------------------
# */ 
    selectStream(3)
    #service type P has a rate of 1/3
    #67% is under the mean: perfect case for a pizza :P
    return Exponential(3)


def NextEvent(events):
    # ---------------------------------------
# * return the index of the next event type
# * ---------------------------------------
# */

    i = 0
    while (events[i].x == 0):       # find the index of the first 'active' */
        i += 1                        # element in the event list            */ 
    #EndWhile
    e = i
    while (i < len(events) - 1):         # now, check the others to find which  */
        i += 1                        # event type is most imminent          */
        if ((events[i].x == 1) and (events[i].t < events[e].t)):
            e = i
    #EndWhile

    return (e)

def FindOne(events, isP = False):
# -----------------------------------------------------
# * return the index of the available server idle longest
# * -----------------------------------------------------
# */
    
    startingPoint = 1
    if (isP): #just changing starting point and end-point
        # in this way, it skips the B-servers and the P-arrival event
        startingPoint += c.SERVERS_B + 1 
        endingPoint = len(events) - 1
    else:
        endingPoint = c.SERVERS_B + 1

    s = -1
    for i in range(startingPoint, endingPoint):
        if (events[i].x == 0): # and (events[i].t < events[s].t)):
                if (s == -1):
                    s = i
                else:
                    if (events[i].t < events[s].t):
                        s = i
    return (s)


def evaluation(listOfSample):
    l = len(listOfSample)
    # costs = [40, 50]
    # gains from each request
    # revenues =[3, 5]
    # rent = 1300
    # computing iva at 22%
    # iva = 22
    titles = ["BAR:\n", "PIZZERIA:\n"]
    global lastArrivalsTime
    global areas
    global indexes
    if l == 1:
        # STEADY ANALISYS
        indexes = listOfSample[0].indexes 
        index = indexes[0] + indexes[1]
        print("\nfor {0:1d} jobs the service node statistics are:\n".format(index))
        stop = c.STOP
    else:
        # TRANSIENT ANALISYS
        print("\n\nTransient analisys:")

        # computing means
        #
        # computing average index 
        tmp = 0
        numSample = len(samplingElementList)

        for i in range(numSample):
            tmp += samplingElementList[i].indexes[0] + \
                samplingElementList[i].indexes[1]
        index = int(tmp / numSample)
        print("\nfor {0:1d} jobs the service node statistics are:\n".format(index))

        # computing average number of elapsed days 
        tmp = 0
        for i in range(numSample):
            tmp += samplingElementList[i].time.day
        stop = int(tmp / numSample)

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
    tmp = lastArrivalsTime[0] - c.START_B
    tmp += 19 * 60 * (stop - 1) 
    lastArrivalsTime[0] = tmp

    tmp = lastArrivalsTime[1] - c.START_P
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
            endPoint = c.SERVERS_B + 1
        else:
            startingPoint = c.SERVERS_B + 1 
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
    rentCost = monthsNum * c.RENT 

    peopleCost= stop * c.COSTS[0] * c.SERVERS_B + stop * c.COSTS[1] * c.SERVERS_P / 2 

    # computing total served requests for each type
    total_B_services = 0
    for s in range(1, c.SERVERS_B + 1):
        total_B_services += sum[s].served

    total_P_services = 0
    for s in range(c.SERVERS_B + 2, len(events) - 1):     #excludin sampling event
        total_P_services += sum[s].served

    # grass revenue 
    revenue = total_B_services * c.REVENUES[0] + total_P_services * c.REVENUES[1]

    # each request costs to restaurant half of its selling cost
    # meaning that if request B costs 3€, it has been bought at 1.50€
    # by restaurant
    materialCost = revenue / 2

    # computing iva at 22%
    ivaCost = revenue * c.IVA / 100

    #computing bill costs
    billCosts = monthsNum * c.BILL_COSTS 

    print("\n\nREVENUE ({0} days):\n".format(stop))
    print("  Gross revenue.. = {0:.2f} €".format(revenue))
    print("  Personal cost.. = {0:.2f} €".format(peopleCost))
    revenue -= peopleCost
    print("  Material cost.. = {0:.2f} €".format(materialCost))
    revenue -= materialCost 
    print("  Rent costs..... = {0:.2f} €".format(rentCost))
    revenue -= rentCost
    print("  Iva costs...... = {0:.2f} €".format(ivaCost))
    revenue -= ivaCost
    print("  Bill costs..... = {0:.2f} €".format(billCosts))
    revenue -= billCosts 
    print("  Revenue........ = {0:.2f} €".format(revenue))



class Event:
    t = None  #next event time
    x = None  #event status, 0 or 1

class Time:
    current = None          # current time in minutes            */
    next = None             # next (most imminent) event time in minutes  */
    day = None              # used to trace all days simulated. The end of
                            # simulation is computed on this value

    dayOfWeek = None        # used to trace week or weekend interarrivals
    # monday = 0            
    # tuesday = 1
    # wednesday = 2
    # thursday = 3
    # friday = 4
    # saturday = 5
    # sunday = 6

    timeSlot = None         # current slot indicator
    
    def __init__(self):
        self.current = c.START_B         
        self.day = 0 
        self.dayOfWeek = 1 # starting from the first working day
        self.timeSlot = 0
        self.notWorkingDays = 0

    def changeSlot(self):
    #   note that t.current cannot be lower than the first element of the
    #   c.SLOTSTIME: t.current is initialized at c.START_B every 'new day starts',
    #   and c.START_B is the first element of c.SLOTSTIME.
        newSlot = 0
        for i in range(1, len(c.SLOTSTIME)):
            # finding the biggest possible slotsTime that is lower than current.
            # if time is equal to slotTime[i], the arrival rate is changed yet.
            if (c.SLOTSTIME[i] <= self.current):
                newSlot = i
            else: #others are bigger 
                break
        self.timeSlot = newSlot

    def copy(self):
        return copy.deepcopy(self)

class AccumSum:
                          # accumulated sums of                */
    service = None          #   service times                    */
    served = None           #   number served                    */

    def copy(self):
        return copy.deepcopy(self)
        

class SamplingElement:
    indexes = None
    lastArrivals = None
    areas = None
    sum = None 
    time = None 
    numeberB = None
    numeberP = None 


    def __init__(self, areas, indexes, lastArrivalsTime, sum, t, numbers):
        newAreas = [i for i in areas]
        self.areas = newAreas

        newIndexes = [i for i in indexes]
        self.indexes = newIndexes

        newArrivals = [i for i in lastArrivalsTime]
        self.lastArrivals = newArrivals

        newSum = []
        for s in range(len(sum)):
            newSum.append(sum[s].copy())
        self.sum = newSum

        self.time = t.copy()

        self.numeberB = numbers[0]
        self.numeberP = numbers[1]


############################Main Program###################################

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
numEvents = c.SERVERS_B + 1 + c.SERVERS_P + 1 + 1
pArrivalIndex = c.SERVERS_B + 1

# The following variables are meant to store the last arrival of each time
# in the last day: in fact, it needs to compute the last arrival time for
# statistical analisys. the compution will be done in the following way:
#   for B type: t.day * 19 * 60 + ( t.lastBTypeArrival - c.START_B )
# in the simulated system, everything happens during the 19 hour between
# 7:00 and 2:00.
# [ lastBTyypeArrival, lastPTypeArrival ]
lastArrivalsTime = [0, 0]
events = [Event() for i in range(numEvents)]
numbers = [0, 0]        # [ numberB, numberP ]: jobs in the node
number = 0              # total number of B and P requests
indexes = [0, 0]        # [ indexB, indexP ]: processed jobs
areas   = [0, 0]         # time integrated number in the node */
sum=[AccumSum() for i in range(0, numEvents - 1)]

samplingElementList = []

initializedP = False #this variable is used to "open door" to P-arrivals

# select time in which sampling events will be scheduled: it will be scheduled
# every day at same time
events[len(events) - 1].t = getSamplingTime()
events[len(events) - 1].x = 1

plantSeeds(0)
events[0].t   = GetArrivalB()
events[0].x   = 1

for s in range(1, numEvents - 1):       #excluding sampling events
    events[s].t     = c.START_B          # this value is arbitrary because */
    events[s].x     = 0              # all servers are initially idle  */
    sum[s].service = 0.0
    sum[s].served  = 0


# t.day < c.STOP and not <= because if you want to perform 365 days starting from
# 0 (t.day is initialized to 0), you have to terminate when the 364th day ends
while (t.day < c.STOP) or (number != 0):
    #initializing sampling

    e = NextEvent(events)                  # next event index */
    t.next = events[e].t                        # next event time  */
    areas[0] += (t.next - t.current) * numbers[0]     # update Bintegral  */
    areas[1] += (t.next - t.current) * numbers[1]     # update Pintegral  */
    t.current = t.next                            # advance the clock*/
    #checking if time slot changed:
    t.changeSlot()

    #check if the pizzeria can open
    if (t.current >= c.START_P) and (not initializedP):
        events[pArrivalIndex].t = GetArrivalP()
        events[pArrivalIndex].x = 1
        initializedP = True

    if (e == 0):                                  # process a B-arrival*/
        numbers[0] += 1

        # if jumped into this block of code, a B type arrival is accepted
        lastArrivalsTime[0] = events[0].t 
        events[0].t = GetArrivalB()

        # close the B-door in two cases: at the end of a day and at the end of
        # simulation
        if (events[0].t > c.STOP_B) or (t.day > c.STOP):
            events[0].x = 0
        #EndIf
        
        if (numbers[0] <= c.SERVERS_B):
            service = GetServiceB()
            s = FindOne(events)
            if (s >= 0):
                sum[s].service += service
                sum[s].served += 1
                events[s].t = t.current + service
                events[s].x = 1
            #Endif
        #EndIf

    #EndIf
    elif (e == pArrivalIndex): # process a P-arrival*/
        numbers[1] += 1

        # if jumped into this block of code, a P type arryval is accepted
        lastArrivalsTime[1] = events[pArrivalIndex].t 
        events[pArrivalIndex].t = GetArrivalP()

        if (events[pArrivalIndex].t > c.STOP_P): 
            events[pArrivalIndex].x = 0
        #EndIf
        
        if (numbers[1] <= c.SERVERS_P):
            service  = GetServiceP()
            s = FindOne(events, True)
            if (s >= 0):
                sum[s].service += service
                sum[s].served += 1
                events[s].t = t.current + service
                events[s].x = 1
        #EndIf
    #EndIf

    elif (e == len(events) - 1):
        # it's a sampling event
        currSample = SamplingElement(areas, indexes, lastArrivalsTime,
                sum, t, numbers)
        samplingElementList.append(currSample)
        events[e].x = 0

    #it's a departure
    else:
        if (e < pArrivalIndex): #B-type
            indexes[0] += 1
            numbers[0] -= 1
            s = e
            if (numbers[0] >= c.SERVERS_B):
                service = GetServiceB()
                sum[s].service += service
                sum[s].served += 1
                events[s].t = t.current + service
            else:
                events[s].x = 0
        else: #P-type
            indexes[1] += 1
            numbers[1] -= 1
            s = e
            if (numbers[1] >= c.SERVERS_P):
                service = GetServiceP()
                sum[s].service += service
                sum[s].served += 1
                events[s].t = t.current + service
            else:
                events[s].x = 0
        
    #EndElse
    number = numbers[0] + numbers[1]
    #it means that a day is over
    if ((events[0].x == 0) and (number == 0)):

        events[len(events) - 1].x = 1
        initializedP = False
        t.current = c.START_B
        c.ARRIVAL_TEMPS = [c.START_B, c.START_P]
        events[0].t = GetArrivalB() 
        events[0].x = 1 
        t.day += 1
        t.dayOfWeek = (t.dayOfWeek + 1) % 7
        

#EndWhile



lastSample = SamplingElement(areas, indexes, lastArrivalsTime, sum, t, numbers)
evaluation([lastSample])
evaluation(samplingElementList)


# create a csv for analisys 
firstLine = "day,# job, # job B, # job P, last arrival B [H], last arrival" + \
        " P [H], area B, area P, revenue B, revenue P, revenue, costs\n"

with open('output/transient.csv', 'w') as transientOut:
    transientOut.write(firstLine)

    precIndexB = 0
    precIndexP = 0
    for i in range(len(samplingElementList)):
        elem = samplingElementList[i]
        day = elem.time.day

        tmpB = elem.indexes[0] 
        tmpP = elem.indexes[1] 
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
        peopleCost = c.COSTS[0] * c.SERVERS_B + \
                c.COSTS[1] * c.SERVERS_P / 2 

        # grass revenue 
        revenueB = jobB * c.REVENUES[0] 
        revenueP = jobP * c.REVENUES[1]
        revenue = revenueB + revenueP 

        # each request costs to restaurant half of its selling cost
        # meaning that if request B costs 3€, it has been bought at 1.50€
        # by restaurant
        materialCost = revenue / 2

        # computing iva at 22%
        ivaCost = revenue * c.IVA / 100

        totCost = peopleCost + materialCost + ivaCost 
        if (stop % 30 == 0):
            totCost += c.RENT
            totCost += c.BILL_COSTS 

        line = \
        '{0},{1},{2},{3},{4:.2f},{5:.2f},{6:.2f},{7:.2f},'. \
        format(day + 1, totalJob, jobB, jobP, lastArrB / 60, lastArrP / 60, areaB,\
                areaP) 
        line += '{0:.2f},{1:.2f},{2:.2f},{3:.2f}'.format(revenueB,\
                revenueP, revenue, totCost)
        if (stop % 30 == 0):
            line += ",# added rent and bill costs"
        line += "\n"
        
        transientOut.write(line)

