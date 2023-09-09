import os
import sys
import sys
sys.path.append('../')
from configurations.Config import config
import re
import pandas as pd
import argparse

def check(theor_l:list, sper_l:list, int_l:list ):
    n = min(len(theor_l), len(sper_l), len(int_l))
    for i in range(n):
        upper = sper_l[i] + int_l[i]
        lower = sper_l[i] - int_l[i]
        theor = theor_l[i]
        theor_in_int = theor < upper and theor > lower
        err = 0
        if not theor_in_int:
            err = min([abs(upper - theor), abs(lower - theor)])
        
        s = f'-slot {i}: theoretical: {theor} & sperimental' 
        if i == n - 2: # gau:
            s += f'_gau: '
        else:
            s+= ': '
        s += f'{sper_l[i]} +/- {int_l[i]} & error: {err} '

        # print(f'-slot {i}: theoretical: {theor} & sperimental: {sper_l[i]} +/- {int_l[i]} & error: {err} ')
        print(s)

def getLastLines(filePath:str, numSample:int = 128):
    lines = {}
    statistics = ['avgInterarrivals','avgWaits','avgNumNodes','avgDelays','avgNumQueues']
    
    df = pd.read_csv(filePath)
    rows = df[df['num. sample'] == numSample]
    for stat in statistics:
        d = dict()
        row = rows[rows['statistic'] == stat]
        d['mean'] = row['mean'].values[0]
        d['conf_int'] = row['w (interval length/2)'].values[0]    
        lines[stat] = d

    return lines

def getTheoreticals(filePath:str):
    theoreticals = {}
    statistics = ['avgInterarrivals','avgWaits','avgNumNodes','avgDelays','avgNumQueues']
    
    theoreticals['week_B'] = dict()
    theoreticals['week_P'] = dict()
    theoreticals['weekend_B'] = dict()
    theoreticals['weekend_P'] = dict()

    for s in statistics:

        # 5 slots, an empty square (2nd slot) + gau + global 
        theoreticals['week_B'][s] = [0 for _ in range(8)]
        theoreticals['week_P'][s] = [0 for _ in range(8)]
        theoreticals['weekend_B'][s] = [0 for _ in range(8)]
        theoreticals['weekend_P'][s] = [0 for _ in range(8)]
        

    df = pd.read_csv(filePath)
    jobType = 'B'
    
    for i in range(2):
        dayType = 'week'

        key = f'{dayType}_{jobType}'
        for j in range(2):
            rows = df[(df['day type'] == dayType) & (df['job type'] == jobType)]
            
            for slot in range(-1, 6):
                if slot == 2:
                    continue
                slot_filtered_rows = rows[rows['slot'] == slot]
                # if jobType == 'P' and slot == 4:
                #     print(rows)
                #     print()
                #     print(slot_filtered_rows)
                #     input()
                if slot_filtered_rows.empty:
                    continue
                for stat in statistics:
                    row = slot_filtered_rows[slot_filtered_rows['statistic'] == stat]
                    
                    val = row['mean'].values[0]
                    theoreticals[key][stat][slot] = val
                    # addig also for gau the global stat
                    if slot == -1:
                        theoreticals[key][stat][-2] = val

            dayType = 'weekend'
            key = f'{dayType}_{jobType}'
        
        jobType = 'P'
        

    return theoreticals

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="check interval support")
    parser.add_argument("-tf", "--theoretical_file", metavar="CSV_FILE", help="specify where theoreticals are stored", required=True)
    parser.add_argument("-gau", "--gaussian", action="store_true", help="use gaussian values in global comparison")
    args = parser.parse_args()

    statistics = ['avgInterarrivals','avgWaits','avgNumNodes','avgDelays','avgNumQueues']
    finiteDirPath = '../output/finite'
    infiniteDirPath = '../output/infinite'
    
    finiteFiles = os.listdir(finiteDirPath)
    infiniteFiles = os.listdir(infiniteDirPath)
    
    theor = getTheoreticals(args.theoretical_file)

    week_B = dict()
    weekend_B = dict()
    week_P = dict()
    weekend_P = dict()
    week_B['name'] = 'week_B'
    weekend_B['name'] = 'weekend_B'
    week_P['name'] = 'week_P'
    weekend_P['name'] = 'weekend_P'

    for s in statistics:
        week_B[s] = {'mean': [0 for _ in range(8)], 'conf_int': [0 for _ in range(8)], 'theoretical': [i for i in theor['week_B'][s]]}
        weekend_B[s] = {'mean': [0 for _ in range(8)], 'conf_int': [0 for _ in range(8)], 'theoretical': [i for i in theor['weekend_B'][s]]}
        week_P[s] = {'mean': [0 for _ in range(8)], 'conf_int': [0 for _ in range(8)], 'theoretical': [i for i in theor['week_P'][s]]}
        weekend_P[s] = {'mean': [0 for _ in range(8)], 'conf_int': [0 for _ in range(8)], 'theoretical': [i for i in theor['weekend_P'][s]]}


    
    for file in finiteFiles:
        # if args.gaussian:
        #     if file == '.gitkeep' or 'gau' not in file:
        #         continue
        # else:
        #     if file == '.gitkeep' or 'gau' in file:
        #         continue
        if file == '.gitkeep':
            continue
        
        filePath = f'{finiteDirPath}/{file}'

        dic = None
        dayType = None
        jobType = None
        if 'weekend' in file:
            dayType = 'weekend'
            if 'B' in file:
                dic = weekend_B
                jobType = 'B'
            else:
                dic = weekend_P
                jobType = 'P'
        else: 
            dayType = 'week'
            if 'B' in file:
                dic = week_B
                jobType = 'B'
            else:
                dic = week_P
                jobType = 'P'
        
        last_run_lines = getLastLines(filePath, config.RUNS)
        index = -1 if not 'gau' in file else -2
        for stat in statistics:
            mean = last_run_lines[stat]['mean']
            conf_int = last_run_lines[stat]['conf_int']

            dic[stat]['mean'][index] = mean
            dic[stat]['conf_int'][index] = conf_int
    



    for file in infiniteFiles:
        if file == '.gitkeep':
            continue
        filePath = f'{infiniteDirPath}/{file}'
        slot = int(re.search(r'\d', file).group())

        dic = None
        dayType = None
        jobType = None
        if 'weekend' in file:
            dayType = 'weekend'
            if 'B' in file:
                dic = weekend_B
                jobType = 'B'
            else:
                dic = weekend_P
                jobType = 'P'
        else: 
            dayType = 'week'
            if 'B' in file:
                dic = week_B
                jobType = 'B'
            else:
                dic = week_P
                jobType = 'P'
        
        last_run_lines = getLastLines(filePath)
        
        for stat in statistics:
            mean = last_run_lines[stat]['mean']
            conf_int = last_run_lines[stat]['conf_int']

            dic[stat]['mean'][slot] = mean
            dic[stat]['conf_int'][slot] = conf_int
    
    
    listOfDic = [week_B, week_P, weekend_B, weekend_P]
    
    for d in listOfDic:

        for stat in statistics:
            name = d['name']
            print(f'\t{name} - {stat}:')
            
            t = d[stat]['theoretical']
            s = d[stat]['mean']
            i = d[stat]['conf_int']
            
            check(t, s, i)

            print()
        print()


