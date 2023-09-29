import sys
sys.path.append('../')

from configurations.Config import config

if __name__ == '__main__':

    # sperimental values for seed 123
    week_numberB = 275
    week_numberP = 41
    weekend_numberB = 395
    weekend_numberP = 116

    # m_b = config.SERVERS_B
    m_b = 3
    m_p = config.SERVERS_P
    # each daily works is 16h. a worker B works for 8 hour. doubling the cost:
    dailyWorkersCost = 2 * m_b * config.WORKERS_COSTS[0] + m_p * config.WORKERS_COSTS[0]
    monthlyWorkersCost = dailyWorkersCost * 28

    monthlyCosts = config.BILL_COSTS + config.SUPPLIERS_COST + config.RENT + monthlyWorkersCost

    for i in range(2):

        title = "\n\nNO GAUSS" if i == 0 else "\n\nGAUSS"
        print(title)
        dailyRevenue_week = week_numberB * config.REVENUES[0] + week_numberP * config.REVENUES[1]
        dailyRevenue_weekend = weekend_numberB * config.REVENUES[0] + weekend_numberP * config.REVENUES[1]

        monthlyRevenue = (5 * dailyRevenue_week + 2 * dailyRevenue_weekend) * 4
        monthlyIva = monthlyRevenue * config.IVA


        print(f'costo mensile: {monthlyCosts}')
        print(f'richieste B: -week: {week_numberB} -weekend: {weekend_numberB}')
        print(f'richieste P: -week: {week_numberP} -weekend: {weekend_numberP}')
        print(f'guadagno mensile: {monthlyRevenue} (iva not included)')
        print(f'iva mensile: {monthlyIva}')
        monthlyRevenue -= monthlyIva
        print(f'guadagno mensile: {monthlyRevenue} (iva included)')
                
        print(f'global revenue: {monthlyRevenue - monthlyCosts}')
        
        # sperimental gaussian values for seed 123
        week_numberB = 77
        week_numberP = 10
        weekend_numberB = 120
        weekend_numberP = 31



