import matplotlib.pyplot as plt
import pandas as pd
import argparse
import os
import re

def makeGraph(filePath:str, statistic:str, theor:float, outputFile:str=None, title:str=None, show:bool=False):
    
    meanColor = [255, 127, 14]

    # Leggi i dati dal file CSV
    if not filePath.endswith('.csv'):
        raise Exception('invalid input file format')

    df = pd.read_csv(filePath)

    filtered_data = df.loc[df['statistic'] == statistic, ['num. sample', 'mean', 'w (interval length/2)']]
    # Estrai le colonne desiderate
    num_sample = filtered_data['num. sample']
    mean = filtered_data['mean']
    # print(inputFile)
    # print(mean)
    # input()
    w = filtered_data['w (interval length/2)']
    #theoretical = pd.Series([float(theor)] * len(num_sample))

    # Crea il grafico
    plt.figure(figsize=(10, 6))
    #plt.plot(num_sample, theoretical, label='Theoretical value', linestyle='--')
    plt.errorbar(num_sample, mean, yerr=w, fmt='o', color=tuple([i/255 for i in meanColor]), label=r'Mean $\pm$ $\omega$')   
    plt.axhline(y=float(theor), linestyle='--', label=f'Theoretical value: {theor}')
    # Aggiungi etichette e titolo
    plt.xlabel('Num. sample')
    
    stat = statistic.strip('avg')
    plt.ylabel(f'{stat}')
    
    if not title:
        fileName = filePath.split('/')[-1]
        title = f'{stat} - {fileName}'
        
    plt.title(title)
    plt.legend()

    # Mostra il grafico
    plt.grid(True)
    if outputFile:
        plt.savefig(outputFile)
    
    if show:
        plt.show()
    else:
        plt.close()

def generateAll():
    statistics = ['avgInterarrivals','avgWaits','avgNumNodes','avgDelays','avgNumQueues']

    week_theoretical_valuesB = {
        'avgInterarrivals': [2.000, 4.762, 0, 2.381, 4.762, 5.882],
        'avgWaits': [2.667, 2.092, 0, 2.428, 2.092, 2.060],
        'avgNumNodes': [1.333, 0.439, 0, 1.020, 0.439, 0.350],
        'avgDelays': [0.667, 0.092, 0, 0.428, 0.092, 0.060],
        'avgNumQueues': [0.333, 0.019, 0, 0.180, 0.019, 0.010],
    }

    week_theoretical_valuesP = {
        'avgInterarrivals': [5.882],
        'avgWaits': [3.209],
        'avgNumNodes': [0.545],
        'avgDelays': [0.209],
        'avgNumQueues': [0.035],
    }
    weekend_theoretical_valuesB = {
        'avgInterarrivals': [2.000, 2.941, 0, 1.333, 2.667, 2.941],
        'avgWaits': [2.667, 2.261, 0, 4.571, 2.327, 2.261],
        'avgNumNodes': [1.333, 0.769, 0, 3.429, 0.873, 0.769],
        'avgDelays': [0.667, 0.261, 0, 2.571, 0.327, 0.261],
        'avgNumQueues': [0.333, 0.089, 0, 1.929, 0.123, 0.089]
    }


    weekend_theoretical_valuesP = {  
        'avgInterarrivals': [2.000],
        'avgWaits': [6.857],
        'avgNumNodes': [3.429],
        'avgDelays': [3.857],
        'avgNumQueues': [1.929],
    }


    week_globalsB = {
        'avgInterarrivals': [3.471],
        'avgWaits': [2.251],
        'avgNumNodes': [0.682],
        'avgDelays': [0.251],
        'avgNumQueues': [0.106],
    }
    
    weekend_globalsB = {
        'avgInterarrivals': [2.413],
        'avgWaits': [2.524],
        'avgNumNodes': [1.102],
        'avgDelays': [0.524],
        'avgNumQueues': [0.273],
    }
    # globalsP == P

    finiteDirPath = '../finite'
    infiniteDirPath = '../infinite'
    
    finiteFiles = os.listdir(finiteDirPath)
    infiniteFiles = os.listdir(infiniteDirPath)


    # finite dir genaration:
    for file in finiteFiles:
        if file == '.gitkeep':
            continue
        print(file)
        path = f'{finiteDirPath}/{file}'
        theoreticals = None
        output = None
        if 'weekend' in file:           
            if 'P' in file:
                output = 'weekend_P'
                theoreticals = weekend_theoretical_valuesP
            else:
                output = 'weekend_B'
                theoreticals = weekend_globalsB
        else:
            if 'P' in file:
                output = 'week_P'
                theoreticals = week_theoretical_valuesP
            else:
                output = 'week_B'
                theoreticals = week_globalsB

        for stat in statistics:
            outputDir = f'finite/{stat}'
            outputName = f'{outputDir}/{output}'
            if 'gau' in file:
                outputName += '_gau'
            if not os.path.exists(outputDir):
                os.makedirs(outputDir)
            makeGraph(path, stat, theoreticals[stat][0], outputName, show=True)


    # infinite dir genaration:
    for file in infiniteFiles:
        if file == '.gitkeep':
            continue
        print(file)
        path = f'{infiniteDirPath}/{file}'

        # retrieve the slot number in the file name
        slot = int(re.search(r'\d', file).group())
        # index for list in the dict. it's different for kind p
        index = slot
        theoreticals = None
        output = None
        if 'weekend' in file:           
            if '_P_' in file:
                output = 'weekend_P'
                theoreticals = weekend_theoretical_valuesP
                index = 0
            else:
                output = 'weekend_B'
                theoreticals = weekend_theoretical_valuesB
        else:
            if '_P_' in file:
                output = 'week_P'
                theoreticals = week_theoretical_valuesP
                index = 0
            else:
                output = 'week_B'
                theoreticals = week_theoretical_valuesB

        output += f'_{slot}'
        for stat in statistics:
            outputDir = f'infinite/slot_{slot}/{stat}'
            outputName = f'{outputDir}/{output}'
            if not os.path.exists(outputDir):
                os.makedirs(outputDir)
            makeGraph(path, stat, theoreticals[stat][index], outputName, show=True)


if __name__ =='__main__':
    parser = argparse.ArgumentParser(description="graphic generator for csv output files")

    parser.add_argument("-a", "--all", action='store_true', help="generate all graphs for files in '../finite/' and '../infinite' and for all statistics. If this option is active, any other option is ignored")

    args, other_args = parser.parse_known_args()
    if args.all:
        generateAll()
    else:

        parser.add_argument("-in", "--input", metavar='INPUT_FILE', required=True, help="specify input csv file")
        parser.add_argument("-s", "--stat", metavar='STATISTIC', required=True, help="specify the statistic for which generate graphic")
        parser.add_argument("-tv", "--theoretical_value", metavar='VALUE', required=True, help="specify the theoretical value")
        parser.add_argument("-out", "--output", metavar='OUTPUT_FILE', help="specify output png file")
        parser.add_argument("-t", "--title", metavar='TITLE', help="specify graph title")

        args = parser.parse_args(other_args)
    
    
        fileName = args.input
        stat = args.stat
        tv = args.theoretical_value
        outputFile = args.output
        title = args.title
        
        makeGraph(fileName, stat, tv, outputFile,title,True)
