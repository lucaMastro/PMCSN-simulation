class Config:

    def __init__(self):
        # time in which arrival rate changes. it is built by taking hours in which
        # rates change and multiplying it by 60 minutes    
        self.SLOTSTIME = [ (i * 60) for i in [7, 11, 15, 18, 19, 23] ]
        self.B_WORKING_HOURS = 16
        self.P_WORKING_HOURS = 4

        # 2:00 am == 26:00. STOP_B = 27 * 60 this is for B-requests
        self.STOP_B = 26 * 60        
        self.STOP_P = self.SLOTSTIME[5]   

        # the bar will close at 15 and will reopen at 18. This means that the first B-Arrival after 
        # that hour will be scheduled at 18 * 60 (min) + Exponential(..). Following variables are for
        # code readability
        self.FIRST_HALFDAY_CLOSE_TIME = self.SLOTSTIME[2]
        self.SECOND_HALFDAY_OPEN_TIME = self.SLOTSTIME[3]

        self.DURATIONS = [(self.SLOTSTIME + [self.STOP_B])[i+1] - (self.SLOTSTIME + [self.STOP_B])[i] \
            for i in range(len(self.SLOTSTIME + [self.STOP_B]) - 1)]


        # initial (open the door) for B requests: 420 [MIN] = 7:00 am 
        self.START_B = self.SLOTSTIME[0]  

        # time in which P arrival process starts
        self.START_P = self.SLOTSTIME[4]
                                 
        #STOP = 365  # terminal (close the door) 
        
        self.SERVERS_B = 2   # number of type B servers
        self.SERVERS_P = 2   # number of type P servers

        #these values will be used for exponential mean, based on the current or next
        #timing, in minutes. the third element is 0 because the bar is closed and its needed 
        # for indexing 
        self.WEEK_LAMBDA_B = [0.5, 0.21, 0, 0.42, 0.21, 0.17]
        self.WEEKEND_LAMBDA_B = [0.5, 0.34, 0, 0.75, 0.375, 0.34]
        self.WEEK_LAMBDA_P = 0.17
        self.WEEKEND_LAMBDA_P = 0.5

        self.MEAN_SERVICE_TIME_B = 2.0
        self.MEAN_SERVICE_TIME_P = 3.0

        self.WORKERS_COSTS = [40, 50]      # € for worker [B, P] per day
        self.REVENUES = [5, 10]     # € for request [B, P]
        self.RENT = 1500           # € for month
        self.IVA = 0.10            # 10%
        self.BILL_COSTS = 2750     # € for month
        self.SUPPLIERS_COST = 2000 # € for month

        self.GAUSSIAN_MEANS_B = [8, 13.5, 0, 18.5, 22.5, 24] # in hours
        self.GAUSSIAN_STD_DEV_B = [1.2, 2, 0, 0.4, 2, 0.9]

        self.GAUSSIAN_MEAN_P = 20.5 
        self.GAUSSIAN_STD_DEV_P = 1

        self.SIMULATE_WEEK = True

        self.DEBUG = False

        self.FINITE_H = False
        self.INFINITE_H = False
        self.FIND_B_VALUE = False
        self.SEED = 0
        self.USE_GAUSSIAN_FACTOR = True
        # batch b keeps the initial values of B for sampling events. If the value for a specific slot
        # does not guarantee the autocorr < THRESHOLD for each stats, it's doubled and it restarts with
        # the new value.
        self.BATCH_B = [1024, 1024, 0, 1024, 1024, 1024]
        self.BATCH_K = 128
        self.RUNS = 1024
        
        self.AUTOCORR_THRESHOLD = 0.2
        self.CONFIDENCE_LEVEL = 0.95

        self.SAMPLING_UNIFORM_A = 1.5
        self.SAMPLING_UNIFORM_B = 2
        # to compute from minutes to hours
        self.CONVERSION_FACTOR = 60

        self.SPLIT_STATS_ANALYSIS_FOR_8_H = True

    def storeConfig(self,outputFileName):
        # Make the file text
        s = f"class Config:\n"
        s += f"    def __init__(self):\n"
        for attr, value in vars(self).items():
            s += f"        self.{attr} = {value}\n"

        with open(f'./configurations/{outputFileName}', 'w') as outputFile:
            outputFile.write(s)


    

config = Config()