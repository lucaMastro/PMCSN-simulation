import support.Config as config
from scipy.stats import norm

class GaussianWeighter:
    # bitmask: in position 0 there will be the normalizer factor of the 0-th slot, that is
    # F(11) - F(7)
    normalizerFactorB = [] 
    normalizerFactorP = 0
    slots = [7, 11, 15, 18, 19, 23, 26] 

    def __init__(self):
        # generating new slotstime list containing also the hour 26 == 02 a.m.:
        

        # find the boundaries of the interval with respect to which to normalize
        # timeSlot is in [0, 5]. 
        # If 0 -> slots[0] - slots[1]  
        # ...
        # If 5 -> slots[5] - slots[6]
        for slotIndex in range(len(self.slots) - 1):
            # slot index = 2 is between 15-18 where the bar is closed. there arent arrivals in that slot 
            # but adding a neutral element (for mul) to keep the same indexing
            if (slotIndex == 2):
                self.normalizerFactorB.append(1)
                continue
            lowerBound = self.slots[slotIndex]
            upperBound = self.slots[slotIndex + 1]

            # getting correctMean
            mu = config.GAUSSIAN_MEANS_B[slotIndex]
            sigma = config.GAUSSIAN_STD_DEV_B[slotIndex]     

            # find normalization value: e.g: F(11) - F(7)
            F_upperBound = norm.cdf(upperBound, loc = mu, scale = sigma)
            F_lowerBound = norm.cdf(lowerBound, loc = mu, scale = sigma)
            normalizationValue = F_upperBound - F_lowerBound 

            self.normalizerFactorB.append(normalizationValue)
        
        # P value inizialitazion
        mu = config.GAUSSIAN_MEAN_P
        sigma = config.GAUSSIAN_STD_DEV_P
        lowerBound = config.START_P / 60
        upperBound = config.STOP_P / 60
        F_upperBound = norm.cdf(upperBound, loc = mu, scale = sigma)
        F_lowerBound = norm.cdf(lowerBound, loc = mu, scale = sigma)
        self.normalizerFactorP = F_upperBound - F_lowerBound 



    def gaussianWeighterFactorB(self, currenTime:float, timeSlot:int):   

        # retrieving correct distribution params
        mu = config.GAUSSIAN_MEANS_B[timeSlot]
        sigma = config.GAUSSIAN_STD_DEV_B[timeSlot]

        # generating new slotstime list containing also the hour 26 == 02 a.m.:
        normalizationValue = self.normalizerFactorB[timeSlot]
            
        # computing the density value

        # again in hours
        t0 = currenTime / 60
        f_t0 = norm.pdf(t0, loc=mu, scale=sigma)
        
        # make the normalization:
        fn_t0 = f_t0 / normalizationValue


        return fn_t0




    def gaussianFactorP(self, currenTime:float):   

        # retrieving correct distribution params
        mu = config.GAUSSIAN_MEAN_P
        sigma = config.GAUSSIAN_STD_DEV_P

        # generating new slotstime list containing also the hour 26 == 02 a.m.:
        normalizationValue = self.normalizerFactorP
            
        # computing the density value

        # again in hours
        t0 = currenTime / 60
        f_t0 = norm.pdf(t0, loc=mu, scale=sigma)
        
        # make the normalization:
        fn_t0 = f_t0 / normalizationValue

        if config.DEBUG:
            print(f'mu = {mu}, sigma = {sigma}')
            print(f't0 = {t0}')
            print(f'f_t0 = {f_t0}')
            print(f'fn_t0 = {fn_t0}')

        return fn_t0
