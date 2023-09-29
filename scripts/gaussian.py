import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import sys
sys.path.append('../')
from support.GaussianWeighter import GaussianWeighter
from configurations.Config import config


def gaussians(mu, sigma, normalizerFactor, lowerBound, upperBound, pizza=False):
    distance = upperBound - lowerBound
    # x range    
    x = np.linspace(mu - distance, mu + distance)

    pdf_values = norm.pdf(x, loc=mu, scale=sigma)
    normalized = pdf_values/normalizerFactor

    # bounds
    plt.axvline(x=lowerBound, color='red', linestyle='--')
    plt.axvline(x=upperBound, color='red', linestyle='--')


    plt.plot(x, pdf_values, label='Gaussian distribution', color='g')
    plt.plot(x, normalized, label='Normalized gaussian distribution', color='b')
    plt.xlabel('Time')
    plt.ylabel('pdf')
    plt.title(f'Gaussian distributions in {lowerBound}:00 - {upperBound}:00')
    plt.grid(True)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True,ncol=2)

    name = f'../relazione/images/{lowerBound}-'
    if upperBound == 26:
        name += '0'
    name += f'{upperBound%24}-gaussian'
    if pizza:
        name += '-pizza'
    name += '.png'
    plt.savefig(name)

    plt.show()

if __name__ == '__main__':

    slots_num = len(config.SLOTSTIME)
    gw = GaussianWeighter()
    for i in range(slots_num):

        if i == 2:
            continue
        
        normalizerFactor = gw.normalizerFactorB[i]
        
        lowerBound = config.SLOTSTIME[i] // config.CONVERSION_FACTOR
        upperBound = None
        if i == slots_num - 1:
            upperBound = config.STOP_B // config.CONVERSION_FACTOR
        else:
            upperBound = config.SLOTSTIME[i + 1] // config.CONVERSION_FACTOR
        
        
        mu = config.GAUSSIAN_MEANS_B[i] 
        sigma = config.GAUSSIAN_STD_DEV_B[i]

        gaussians(mu,sigma,normalizerFactor,lowerBound, upperBound)

    mu = config.GAUSSIAN_MEAN_P
    sigma = config.GAUSSIAN_STD_DEV_P
    lowerBound = config.START_P // config.CONVERSION_FACTOR
    upperBound = config.STOP_P // config.CONVERSION_FACTOR

    gaussians(mu,sigma,normalizerFactor,lowerBound, upperBound, True)
