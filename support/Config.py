# time in which arrival rate changes. it is built by taking hours in which
# rates change and multiplying it by 60 minutes    
SLOTSTIME = [ (i * 60) for i in [7, 11, 15, 18, 19, 23] ]
B_WORKING_HOURS = 16
P_WORKING_HOURS = 4

# the bar will close at 15 and will reopen at 18. This means that the first B-Arrival after 
# that hour will be scheduled at 18 * 60 (min) + Exponential(..). Following variables are for
# code readability
FIRST_HALFDAY_CLOSE_TIME = SLOTSTIME[2]
SECOND_HALFDAY_OPEN_TIME = SLOTSTIME[3]


# initial (open the door) for B requests: 420 [MIN] = 7:00 am 
START_B = SLOTSTIME[0]  

# time in which P arrival process starts
START_P = SLOTSTIME[4]

# 3:00 am == 27:00. STOP_B = 27 * 60 this is for B-requests
STOP_B = 27 * 60        
STOP_P = SLOTSTIME[5]                                    
#STOP = 365  # terminal (close the door) 
STOP = 128  # terminal (close the door) 
SERVERS_B = 2   # number of type B servers
SERVERS_P = 2   # number of type P servers

#these values will be used for exponential mean, based on the current or next
#timing, in minutes. the third element is 0 because the bar is closed and its needed 
# for indexing 
WEEK_LAMBDA_B = [0.5, 0.21, 0, 0.42, 0.21, 0.17]
WEEKEND_LAMBDA_B = [0.5, 0.34, 0, 0.75, 0.375, 0.34]
WEEK_LAMBDA_P = 0.17
WEEKEND_LAMBDA_P = 1

MEAN_SERVICE_TIME_B = 2
MEAN_SERVICE_TIME_P = 3

COSTS = [40, 50]
REVENUES = [4, 7]
RENT = 1500         # € for month
IVA = 0.22            # 22%
BILL_COSTS = 2000   # € for month

GAUSSIAN_MEANS_B = [8, 13.5, 0, 18.5, 22.5, 24] # in hours
GAUSSIAN_STD_DEV_B = [1.2, 2, 0, 0.4, 2, 0.9]

GAUSSIAN_MEAN_P = 20.5 
GAUSSIAN_STD_DEV_P = 1

SIMULATE_WEEK = True

DEBUG = True