from math import factorial

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

    


if __name__ == '__main__':

    #lambda_ = 1/float(input('give me interarrival time: '))
    #mi = float(input('give me service rate: '))
    #m = int(input('give me server s number: '))
    
    typeP = True
#    typeP = False

    if (not typeP):
        # typeB
        fasce = config.SLOTS_DURATION_B  
        #fasce = [(i * 60) for i in [3, 3, 5, 2, 2, 4]]
        dayDuration = 19 #h
        interarrivalsWeek = 1 / config.WEEK_LAMBDA_B 
        interarrivalsWeekEnd = 1 / config.WEEKEND_LAMBDA_B
        mi = 0.5
        m = 2

    else:
        # typeP
        fasce = [2]
        dayDuration = 2 #h
        interarrivalsWeek = [1 / config.WEEK_LAMBDA_P] 
        interarrivalsWeekEnd = [1 / config.WEEKEND_LAMBDA_P]
        mi = 1/3 
        m = 2

    P0_week = []
    PQ_week = []
    rho_week = []
    E_TQ_week = []
    E_NQ_week = []
    E_Si_week = []
    E_S_week = []
    E_TS_week = []

    P0_weekEnd = []
    PQ_weekEnd = []
    rho_weekEnd = []
    E_TQ_weekEnd = []
    E_NQ_weekEnd = []
    E_Si_weekEnd = []
    E_S_weekEnd = []
    E_TS_weekEnd = []
    
    for i in range(2):
        if i == 0:
            interarrivals = interarrivalsWeek 
            pos = P0_week
            pqs = PQ_week
            rhos = rho_week
            etqs = E_TQ_week
            enqs = E_NQ_week
            esis = E_Si_week
            ess = E_S_week
            etss = E_TS_week
            print('\nWEEK ANALISYS:')
        else:
            interarrivals = interarrivalsWeekEnd 
            pos = P0_weekEnd
            pqs = PQ_weekEnd
            rhos = rho_weekEnd
            etqs = E_TQ_weekEnd
            enqs = E_NQ_weekEnd
            esis = E_Si_weekEnd
            ess = E_S_weekEnd
            etss = E_TS_weekEnd
            print('\nWEEKEND ANALISYS:')

        for j in range(len(interarrivals)):
            print("\nfascia oraria: {0}".format(j+1))
            lambda_ = 1 /interarrivals[j]

            rho = compute_RHO(lambda_, m, mi)

            P0 = compute_P0(m,rho)
            PQ = compute_PQ(m, rho)
            ES = compute_ES(m,mi)
            E_TQ = PQ * ES / (1 - rho)
            E_NQ = lambda_ * E_TQ 

            E_Si = 1 / mi

            E_T = E_TQ + E_Si  


            pos.append(P0)
            pqs.append(PQ)
            rhos.append(rho)
            ess.append(ES)
            etqs.append(E_TQ)
            enqs.append(E_NQ)
            esis.append(E_Si)
            etss.append(E_T)


            print('Rho = {0:.2f}'.format(rho))
            print('PQ = {0:.2f}'.format(PQ))
            print('P0 = {0:.2f}'.format(P0))
            print('E(TQ) = {0:.2f}'.format(E_TQ))
            print('E(NQ) = {0:.2f}'.format(E_NQ))
            print('E(Si) = {0:.2f}'.format(E_Si))
            print('E(S) = {0:.2f}'.format(1/(m*mi)))
            print('E(TS) = {0:.2f}'.format(E_T)) 

    

    print("\nValori medi:")

    #lamda:
    lambdasWeek = [1/i for i in interarrivalsWeek ]
    lambdasWeekEnd = [1/i for i in interarrivalsWeekEnd ]
    
    tmp = 0
    sum = 0
    for i in range(len(fasce)):
        tmp += (lambdasWeek[i] * fasce[i])
    sum += tmp
    tmp = 0
    for i in range(len(fasce)):
        tmp += (lambdasWeekEnd[i] * fasce[i])
   
    sum = sum * 5 + tmp * 2
    
    mean_lambda_job_on_min = sum / (7 * dayDuration * 60)
    print('mean_lambda = {0:.2f} j/min'.format(mean_lambda_job_on_min))
    print('mean_interarrival = {0:.2f} min'.format(1/mean_lambda_job_on_min))

    #ENQ
    sum = 0
    tmp = 0
    for i in range(len(fasce)):
        tmp += (E_NQ_week[i] * fasce[i])/(dayDuration * 60)

    sum += tmp
    tmp = 0
    for i in range(len(fasce)):
        tmp += (E_NQ_weekEnd[i] * fasce[i])/(dayDuration * 60)
    print(tmp)
    sum = 5 * sum + 2*tmp 
    sum /= 7
    print("E(NQ) = {0:.2f}".format(sum))

    eTQ = sum / mean_lambda_job_on_min
    print('E(TQ) = {0:.2f}'. format(eTQ))
    eS = 1/mi
    print('E(S) = {0:.2f}'.format(eS))
    ets = eS + eTQ
    print('E(TS) = {0:.2f}'. format(ets))
    print('E(NS) = {0:.2f}'. format(ets * mean_lambda_job_on_min))
    print('rho = {0:.2f}'. format(mean_lambda_job_on_min / (m * mi)))



