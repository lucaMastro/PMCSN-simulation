from math import factorial

import argparse
import importlib
import os
import sys
sys.path.append('../')

from configurations.Config import config

def compute_P0(m, rho):
    sum = 0
    for i in range(0, m):
        sum += pow(m * rho, i) / factorial(i)
    
    sum += pow(m * rho, m) / (factorial(m) * (1 - rho))
    p0 = 1/sum
    return p0


def compute_PQ(m, rho):
    tmp = pow(m * rho, m) / (factorial(m) * (1 - rho))
    pq = tmp * compute_P0(m, rho)
    
    return pq

def compute_RHO(lambda_, m, mi):
    rho = lambda_ /(m * mi)
    return rho

def compute_ES(m, mi):
    return 1/(m * mi)

def debug(a):
    for i in a:
        print(i)
    input()

    

def compute(interarrivals:list, m:int, mi:float):

    d = {
        'P0' : [],
        'PQ' : [],
        'rho' : [],
        'E_TQ' : [],
        'E_NQ' : [],
        'E_Si' : [],
        'E_S' : [],
        'E_TS' : []
    }

    numSlot = len(interarrivals)
    for j in range(numSlot):

        lambda_ = 1 /interarrivals[j]

        rho = compute_RHO(lambda_, m, mi)

        P0 = compute_P0(m, rho)
        PQ = compute_PQ(m, rho)
        ES = compute_ES(m, mi)
        E_TQ = PQ * ES / (1 - rho)
        E_NQ = lambda_ * E_TQ 
        E_Si = 1 / mi
        E_TS = E_TQ + E_Si  


        d['P0'].append(P0)
        d['PQ'].append(PQ)
        d['rho'].append(rho)
        d['E_S'].append(ES)
        d['E_TQ'].append(E_TQ)
        d['E_NQ'].append(E_NQ)
        d['E_Si'].append(E_Si)
        d['E_TS'].append(E_TS)

    return d
    
def printSlotStatistic(dic:dict):
    slotsNum = len(config.WEEKEND_LAMBDA_B)
    for i in range(slotsNum):
        for k in dic.keys():
            value = dic[k]
            print(f"\nSLOT: {i + 1}:")
            print(f'{k}: {value}')
    
            
def loadPersonalConfig(filePath):
    global config
    try:
        # get the dir and append in the path
        dir=os.path.dirname(filePath)
        sys.path.append(dir)
        
        # removing extension from filePath:
        moduleName = os.path.splitext(filePath)[0].split('/')[-1]
        newConfig = importlib.import_module(moduleName)
        config = newConfig.Config()
        
    except Exception as e:
        print(e)
        raise argparse.ArgumentTypeError("Invalid file.")


def makeComputation(outputFile:str=None):
    global etq
    global ets
    global enq
    global ens
    global lambdas
    global m
    global s_i
    global durations
    global day_durations
    global l
    global tq
    global ts
    global nq
    global ns
    for i in range(len(durations)):
    
        l = lambdas[i]
        s = s_i/m
        rho = l * s


        tq = compute_PQ(m, rho) * s / (1 - rho)
        ts = tq + s_i
        # little
        nq = l * tq
        ns = l * ts

        if not outputFile:
            print(f'slot: {i + 1}\n\tinterarr = {1/l:.3f}\n\tTS = {ts:.3f}\n\tNS = {ns:.3f}\n\tTQ = {tq:.3f}\n\tNQ = {nq:.3f}\n')
        etq.append(tq)
        ets.append(ts)
        enq.append(nq)
        ens.append(ns)
    
    
    l = sum([li * d for li,d in zip(lambdas, durations)]) / day_durations
    tq = sum([t * d for t,d in zip(etq, durations)]) / day_durations
    ts = sum([t * d for t,d in zip(ets, durations)]) / day_durations
    nq = sum([t * d for t,d in zip(enq, durations)]) / day_durations
    ns = sum([t * d for t,d in zip(ens, durations)]) / day_durations
    if not outputFile:
        print("global averaged stats:\n")
        print(f'\tinterarr = {1/l:.3f}\n\tTS = {ts:.3f}\n\tNS = {ns:.3f}\n\tTQ = {tq:.3f}\n\tNQ = {nq:.3f}')
    
    else:
        writeToFile(outputFile)


def writeToFile(outputFile:str):
    global week
    global B 
    global etq
    global ets
    global enq
    global ens
    global lambdas
    global m
    global s_i
    global durations
    global day_durations
    global l
    global tq
    global ts
    global nq
    global ns

    if not outputFile.endswith('.csv'):
        outputFile += ".csv"
    
    legend = None
    if not os.path.exists(outputFile):
        legend = 'day type,job type,slot,statistic,mean\n'

    statistics = ['avgInterarrivals','avgWaits','avgNumNodes','avgDelays','avgNumQueues']
    dic = {
        'avgInterarrivals': [1/li for li in lambdas],
        'avgWaits': ets,
        'avgNumNodes': ens,
        'avgDelays': etq,
        'avgNumQueues': enq,
    }
    dic_globals = {
        'avgInterarrivals': 1/l,
        'avgWaits': ts,
        'avgNumNodes': ns,
        'avgDelays': tq,
        'avgNumQueues': nq,
    }

    with open(outputFile, 'a') as file:
        
        if legend:
            file.write(legend)
        
        for i in range(len(etq)):
            dayType = 'week' if week else 'weekend'
            jobType = 'B' if B else 'P'
            index = i if i < 2 else i + 1
            index = 4 if jobType == 'P' else index
            
            for stat in statistics:
                s = f'{dayType},{jobType},{index},{stat},{dic[stat][i]:.3f}\n'
                file.write(s)
    
        # write globals
        for stat in statistics:
            s = f'{dayType},{jobType},-1,{stat},{dic_globals[stat]:.3f}\n'
            file.write(s)




if __name__ == '__main__':
    global week
    global B 
    global etq
    global ets
    global enq
    global ens
    global lambdas
    global m
    global s_i
    global durations
    global day_durations
    global l
    global tq
    global ts
    global nq
    global ns


    parser = argparse.ArgumentParser(description="theoretical value support")
    parser.add_argument("-w", "--week", action="store_true", help="specify week values")
    parser.add_argument("-we", "--week_end", action="store_true", help="specify week-end values")
    parser.add_argument("-b", "--b_type", action="store_true", help="specify B type values")
    parser.add_argument("-p", "--p_type", action="store_true", help="specify P type values")
    parser.add_argument("-cf", "--config_file", metavar="PATH_TO_CONFIG_FILE", help="specify the file wich contains system params")
    parser.add_argument("-sf", "--store_file", metavar="STORE_FILE", help="specify the file .csv in wich store all values")


    iterations = 1
    output = None

    args = parser.parse_args()

    if args.config_file:
        configFilePath = args.config_file
        loadPersonalConfig(configFilePath)

    if args.store_file:
        iterations = 4
        output = args.store_file
        args.week = True
        args.week_end = False
        args.b_type = True
        args.p_type = False

    for i in range(iterations):
        etq = []
        ets = []
        enq = []
        ens = []
        lambdas = None
        m = None
        s_i = None
        durations = None
        day_durations = None

        if args.week:
            week = True
            if args.b_type:
                B = True
                lambdas = [i for i in config.WEEK_LAMBDA_B]
            else: 
                lambdas = [config.WEEK_LAMBDA_P]
                B = False
        elif args.week_end:
            week = False
            if args.b_type:
                lambdas = [i for i in config.WEEKEND_LAMBDA_B]
                B = True
            else:
                lambdas = [config.WEEKEND_LAMBDA_P]
                B = False
        



        if args.b_type:
            m = config.SERVERS_B
            s_i = config.MEAN_SERVICE_TIME_B
            durations = [i for i in config.DURATIONS]

        elif args.p_type:
            m = config.SERVERS_P
            s_i = config.MEAN_SERVICE_TIME_P
            durations = [config.DURATIONS[i] for i in range(4,5)]

        if (args.b_type):
            lambdas.pop(2)
            durations.pop(2)
        day_durations = sum(durations)


        """ 

        for i in range(len(durations)):
        
            l = lambdas[i]
            s = s_i/m
            rho = l * s


            tq = compute_PQ(m, rho) * s / (1 - rho)
            ts = tq + s_i
            # little
            nq = l * tq
            ns = l * ts

            print(f'slot: {i + 1}\n\tinterarr = {1/l:.3f}\n\tTS = {ts:.3f}\n\tNS = {ns:.3f}\n\tTQ = {tq:.3f}\n\tNQ = {nq:.3f}\n')
            etq.append(tq)
            ets.append(ts)
            enq.append(nq)
            ens.append(ns)
        
        
        
        print("global averaged stats:\n")
        l = sum([li * d for li,d in zip(lambdas, durations)]) / day_durations
        tq = sum([t * d for t,d in zip(etq, durations)]) / day_durations
        ts = sum([t * d for t,d in zip(ets, durations)]) / day_durations
        nq = sum([t * d for t,d in zip(enq, durations)]) / day_durations
        ns = sum([t * d for t,d in zip(ens, durations)]) / day_durations
        print(f'\tinterarr = {1/l:.3f}\n\tTS = {ts:.3f}\n\tNS = {ns:.3f}\n\tTQ = {tq:.3f}\n\tNQ = {nq:.3f}')

    """

        
        makeComputation(output)

        # in odd iteration: change the job type
        # in even iteration: change the day type
        if i % 2 == 0:
            args.b_type = not args.b_type
            args.p_type = not args.p_type
        else:
            args.b_type = not args.b_type
            args.p_type = not args.p_type
            args.week = not args.week
            args.week_end = not args.week_end

        #print(f'restart: args.b_type: {args.b_type}, args.p_type: {args.p_type}, args.week: {args.week}, args.weekend: {args.weekend} ')
            