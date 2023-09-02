from math import factorial
from configurations.Config import config
import argparse

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
    
            



if __name__ == '__main__':


    etq = []
    ets = []
    enq = []
    ens = []
    lambdas = None
    m = None
    s_i = None
    durations = None
    day_durations = None

    parser = argparse.ArgumentParser(description="theoretical value support")
    parser.add_argument("-w", "--week", action="store_true", help="specify week values")
    parser.add_argument("-we", "--week_end", action="store_true", help="specify week-end values")
    parser.add_argument("-b", "--b_type", action="store_true", help="specify B type values")
    parser.add_argument("-p", "--p_type", action="store_true", help="specify P type values")

    args = parser.parse_args()
    if args.week:
        if args.b_type:
            lambdas = [i for i in config.WEEK_LAMBDA_B]
        else: 
            lambdas = [config.WEEK_LAMBDA_P]
    elif args.week_end:
        if args.b_type:
            lambdas = [i for i in config.WEEKEND_LAMBDA_B]
        else:
            lambdas = [config.WEEKEND_LAMBDA_P]
    



    if args.b_type:
        m = config.SERVERS_B
        s_i = config.MEAN_SERVICE_TIME_B
        durations = [i for i in config.DURATIONS]
        print(f'durations: {durations}')
    elif args.p_type:
        m = config.SERVERS_P
        s_i = config.MEAN_SERVICE_TIME_P
        durations = [config.DURATIONS[i] for i in range(4,5)]

    if (args.b_type):
        lambdas.pop(2)
        durations.pop(2)
    day_durations = sum(durations)

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
    print(f'\tinterarr = {1/l:.3f}\n\tTS = {ts:.3f}\n\tNS = {ns:.3f}\n\tTQ = {tq:.3f}\n\tNQ = {nq:.3f}\n')



