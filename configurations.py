# time in which arrival rate changes. it is built by taking hours in which
# rates change and multiplying it by 60 minutes
SLOTSTIME = [ (i * 60) for i in [7, 13, 18, 20, 22] ]

SLOTS_DURATION_B = [(i * 60) for i in [6, 5, 2, 2, 4]]
SLOTS_DURATION_P = [120]

START_B = SLOTSTIME[0]  # initial (open the door) for B requests:
                        # 420 [MIN] = 7:00 am 
START_P = SLOTSTIME[3]  # open the door for P requests:
                        # 1200 MIN = 20:00
STOP_B = 26 * 60        # 2:00 am == 26:00. STOP_B = 26 * 60
                        # this is for B-requests
STOP_P = SLOTSTIME[4]
                                    
STOP = 365  # terminal (close the door) time [DAYS]

SERVERS_B = 2   # number of type B servers
SERVERS_P = 2   # number of type P servers

ARRIVAL_TEMPS = [START_B, START_P]

#these values will be used for exponential mean, based on the current or next
#timing 
WEEK_INTERARRIVAL_B = [6, 12, 4, 6, 6]
WEEKEND_INTERARRIVAL_B = [4, 6, 3, 4, 2]
WEEK_INTERARRIVAL_P = 6
WEEKEND_INTERARRIVAL_P = 3/2

COSTS = [40, 50]
REVENUES = [4, 7]
RENT = 1500         # € for month
IVA = 22            # 22%
BILL_COSTS = 2000   # € for month

