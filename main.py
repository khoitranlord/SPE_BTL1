import random
import math
import numpy as np
from customer import Customer
from simulations import *
from MMCKQueue import *
from threading import Thread, Lock

#arrival = 0.05 , service rate = 0.05, # servers  = 5;
#arrival = 0.1 , service rate = 0.2, # servers  = 5;

#arrival = 0.1 , service rate = 0.1, # servers  = 5;
#0.1 / 5*0.1 = 0.2
if __name__ == '__main__':
    totalServedCustomers = 0
    queueLock = Lock()
    printLock = Lock()
    entranceCustomerEvent = CustomerEvent(0.1, queueLock)
    foodCustomerEvent = CustomerEvent(0.05, queueLock)
    drinkCustomerEvent = CustomerEvent(0.05, queueLock)


    simulationTime = 200000
    
    entranceCustomerEvent.timeGenerate(simulationTime = simulationTime, arrivalTime = 0)
    
    drinkMMCK = MMCKQueue("drink_queue",0.04, 10, 15, drinkCustomerEvent, waitCustomerFromOtherQueue = True, queueLock = queueLock, printLock = printLock)
    foodMMCK = MMCKQueue("food_queue",0.03, 10, 15, foodCustomerEvent, waitCustomerFromOtherQueue = True, queueLock = queueLock, printLock = printLock)
    entranceMMCK= MMCKQueue("entrance_queue",0.1, 5, 15, entranceCustomerEvent, nextQueueList = [ foodMMCK, drinkMMCK], queueRatio = [1, 1], queueLock = queueLock, printLock = printLock)
    
    
    # print(len(entranceMMCK.customerEventSim.eventList),' customer go to entrance', entranceMMCK.customerEventSim.eventList)
    
    
    threads     = [None, None, None]
    threads[0]  = Thread(target=entranceMMCK.run, args=(simulationTime, ))
    threads[1]  = Thread(target=drinkMMCK.run, args=(simulationTime, ))
    threads[2]  = Thread(target=foodMMCK.run, args=(simulationTime, ))
    
    for thread in threads:
        thread.start()
        
        
    # while True:    
    #    if entranceMMCK.queueStatus == QueueStatus.IDLE and drinkMMCK.queueStatus == QueueStatus.IDLE and foodMMCK.queueStatus == QueueStatus.IDLE:
    #         entranceMMCK.stop()
    #         drinkMMCK.stop()
    #         foodMMCK.stop()
    #         break
        
    
   
    for thread in threads:
        thread.join()
