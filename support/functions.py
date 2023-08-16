from support.rngs import random, selectStream
from math import log
import support.Config as config
from support.Time import Time
from support.Statistics import Statistics

# initialize configurations

def Uniform(a,b):  
# --------------------------------------------
# * generate a Uniform random variate, use a < b 
# * --------------------------------------------
# */
  return (a + (b - a) * random())  


def Exponential(m):
# ---------------------------------------------------
# * generate an Exponential random variate, use m > 0.0 
# * ---------------------------------------------------
# */
    return (-m * log(1.0 - random()))


def getSamplingTime():
    selectStream(4) 
    # choosing a value between 20 and 22: otherwise P-type variables may not 
    # be sampled
    return (Uniform(config.SLOTSTIME[len(config.SLOTSTIME) - 2], 
        config.SLOTSTIME[len(config.SLOTSTIME) - 1]))

def getCorrectLambdaB(time:Time):
    # time: current instance of class Time
    # checking if it's a weekend:
    m = 0
    if (time.dayOfWeek):
        m = config.WEEK_LAMBDA_B[time.timeSlot]
    else: # week day
        m = config.WEEKEND_LAMBDA_B[time.timeSlot]
    return m
    


def getCorrectLambdaP(time:Time):
    # time: current instance of class Time
    # checking if it's a weekend:
    m = 0
    if (time.dayOfWeek):
        m = config.WEEK_LAMBDA_P
    else: # week day
        m = config.WEEKEND_LAMBDA_P
    return m
    



def GetArrivalB(meanTime:int):
# ---------------------------------------------
# * generate the next arrival time, with rate 1/2
# * ---------------------------------------------
# */  
    selectStream(0) 
    #m = getCorrectInterarrival(time)
    return Exponential(meanTime)
    


def GetArrivalP(meanTime:int):
# ---------------------------------------------
# * generate the next arrival time, with rate 1/2
# * ---------------------------------------------
# */ 
    selectStream(1) 
    #m = getCorrectInterarrival(time, True)
    #print(t.dayOfWeek, t.current, m)
    return Exponential(meanTime)
     


def GetServiceB():
# --------------------------------------------
# * generate the next service time with rate 1/6
# * --------------------------------------------
# */ 
    selectStream(2)
    #service type B has a rate of 1/2
    return Exponential(config.MEAN_SERVICE_TIME_B)
  
def GetServiceP():
# --------------------------------------------
# * generate the next service time with rate 1/6
# * --------------------------------------------
# */ 
    selectStream(3)
    #service type P has a rate of 1/3
    #67% is under the mean: perfect case for a pizza :P
    return Exponential(config.MEAN_SERVICE_TIME_P)


def NextEvent(events):
    # * ---------------------------------------
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


def FindOneB(events):
    # -----------------------------------------------------
    # * return the index of the available server idle longest
    # * -----------------------------------------------------
    # */
    
    # following are defined to slice between B servers
    startingPoint = 1
    endingPoint = config.SERVERS_B + 1
    s = -1
    for idx, event in enumerate(events):
        """ 
        this line is added to keep the same idx notation of event list:
        doing events[startingPoint:endingPoint] the idx == 1 will correspond
        to the server in event[2]
        """
        if idx not in range(startingPoint,endingPoint):
            continue
        if event.x == 0:  # Check if the server is available (idle)
            if s == -1 or events[idx].t < events[s].t:
                s = idx
    return s

def FindOneP(events):
    # -----------------------------------------------------
    # * return the index of the first available server
    # * -----------------------------------------------------
    # */
    
    startingPoint = config.SERVERS_B + 2 
    endingPoint = len(events)
    s = -1
    for i in range(startingPoint, endingPoint):
        if (events[i].x == 0):
                s = i
                break
    return s

