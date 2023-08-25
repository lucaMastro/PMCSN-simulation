from math import factorial
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
    slotsNum = len(config.WEEK_LAMBDA_B)
    for i in range(slotsNum):
        for k in dic.keys():
            value = dic[k]
            print(f"\nSLOT: {i + 1}:")
            print(f'{k}: {value}')
    
            



if __name__ == '__main__':

    #lambda_ = 1/float(input('give me interarrival time: '))
    #mi = float(input('give me service rate: '))
    #m = int(input('give me server s number: '))
    

    # typeB
    slotsDurationB = []
    for i in range(len(config.WEEK_LAMBDA_B) - 1):
        slotsDurationB.append(config.SLOTSTIME[i + 1] - config.SLOTSTIME[i])

    interarrivalsWeek = [1 /i for i in config.WEEK_LAMBDA_B] 
    interarrivalsWeekEnd = [1 /i for i in config.WEEKEND_LAMBDA_B]
    mi = config.MEAN_SERVICE_TIME_B
    m = config.SERVERS_B
   
    B_week = compute(interarrivalsWeek, m, mi)
    B_weekEnd = compute(interarrivalsWeekEnd, m, mi)

    # typeP
    interarrivalsWeek = [1 / config.WEEK_LAMBDA_P] 
    interarrivalsWeekEnd = [1 / config.WEEKEND_LAMBDA_P]
    mi = config.MEAN_SERVICE_TIME_P
    m = config.SERVERS_P
    
    P_week = compute(interarrivalsWeek, m, mi)
    P_weekEnd = compute(interarrivalsWeekEnd, m, mi)

    
    printSlotStatistic(B_week)
    printSlotStatistic(B_weekEnd)
    printSlotStatistic(P_week)
    printSlotStatistic(P_weekEnd)

    

    print("\nValori medi B su tutte le fasce:\n")

    #lamda:
    
    meanLambdaWeek = sum(l * duration for l, duration in zip(config.WEEK_LAMBDA_B, slotsDurationB) )
    meanLambdaWeekEnd = sum(l * duration for l, duration in zip(config.WEEKEND_LAMBDA_B, slotsDurationB) )
    
    print(f'mean_lambda week= {meanLambdaWeek:.2f} j/min')
    print(f'mean_lambda weekend = {meanLambdaWeekEnd:.2f} j/min')

    #ENQ
    meanNQweek = sum(l * duration for l, duration in zip(B_week['E_NQ'], slotsDurationB) )
    meanNQweekEnd = sum(l * duration for l, duration in zip(B_weekEnd['E_NQ'], slotsDurationB) )
    
    print(f'mean_NQ week= {meanNQweek:.2f} j')
    print(f'mean_NQ weekend = {meanLambdaWeekEnd:.2f} j')
    
    # ETQ
    etq_week = meanNQweek/meanLambdaWeek
    etq_weekend = meanLambdaWeekEnd/meanLambdaWeekEnd
    print(f'mean_TQ week= {etq_week:.2f} s')
    print(f'mean_TQ weekend = {etq_weekend:.2f} s')

    # ES
    es = 1/mi
    print(f'E(S) = {es:.2f} s')
    
    # ETS
    ets_week = es + etq_week
    ets_weekend = es + etq_weekend
    print(f'meanResponseTime week = {etq_week:.2f} s')
    print(f'meanResponseTime weekend = {etq_weekend:.2f} s')
    
    # ENS
    print(f'meanNumberInCenter week = {ets_week * meanLambdaWeek:.2f}')
    print(f'meanNumberInCenter weekend = {ets_weekend * meanLambdaWeekEnd:.2f}')
    



