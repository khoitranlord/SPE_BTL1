import random
import queue
from customer import CustomerStatus, Customer
from simulations import CustomerEvent
from enum import Enum
from threading import Thread, Lock

class QueueStatus(Enum):
    WORKING = "working"
    STOP = "stop"

'''
    waiting time : wait in queue
    service time : 
    response time: spent in system = waiting time + service time
'''

class MMCKQueue:
    def __init__(
        self,
        name,
        service_rate,
        serverNum,
        capacity,
        customerEventSim,
        nextQueueList=None,
        queueRatio=None,
        waitCustomerFromOtherQueue = False
    ):
        self.name = name
        self.service_rate = service_rate
        self.maxCapacity = capacity
        self.serverNum = serverNum
        self.currentTime = 0
        self.previousTime = 0
        self.availableServers = serverNum
        self.customerEventSim = customerEventSim
        self.waitingQueue = queue.Queue(self.maxCapacity - self.serverNum)
        self.servingNum = 0
        self.totalServedCustomers = 0
        self.totalWaitingTime = 0
        self.totalQueueTime = 0
        self.avgWaitLen = 0  # Corrected variable name
        self.avgWaitQuLen = 0
        self.avgWaitTime = 0
        self.avgWaitQuTime = 0
        self.nextQueueList = nextQueueList
        self.queueRatio = queueRatio
        self.queueStatus = QueueStatus.WORKING
        self.waitCustomerFromOtherQueue = waitCustomerFromOtherQueue
        self.lock = Lock()

    def arrival(self, customerEvent):
        if self.availableServers > 0:
            # Start serving the customer
            tempServiceTime = int(random.expovariate( self.service_rate) )
            customerEvent.arrivalTime += tempServiceTime
            customerEvent.CustomerStatus = CustomerStatus.DEPART
            self.customerEventSim.addCustomerEvent(customerEvent)
            self.totalWaitingTime += tempServiceTime
            self.servingNum += 1
            self.availableServers -= 1
            # print("\nCustomer arrive at queue ", self.name)
        else:
            # No available server, add the customer to the waiting queue
            self.waitingQueue.put(customerEvent)
            # print("\nCustomer gets back to the waiting queue at queue ", self.name)

    def depart(self, customerEvent):
        # Check if there is any customer in the waiting queue
        if not self.waitingQueue.empty():
            # Start serving the next customer
            nextCustomerEvent = self.waitingQueue.get()
            service_time = int(random.expovariate( self.service_rate) )
            nextCustomerEvent.arrivalTime = self.currentTime + service_time
            nextCustomerEvent.CustomerStatus = CustomerStatus.DEPART
            self.customerEventSim.addCustomerEvent(nextCustomerEvent)
            self.servingNum -= 1
            self.availableServers += 1  # Corrected variable name
            # self.queueStatus = QueueStatus.IDLE
        else:
            # No customer in the waiting queue, increase the number of available servers
            self.servingNum -= 1
            self.availableServers += 1
            # self.queueStatus = QueueStatus.IDLE
        self.totalServedCustomers += 1
        # Customer departs to other queues.
        if self.nextQueueList is not None:  # Corrected comparison
            #random.seed(42)
            random.shuffle(self.nextQueueList)
            selectedNextQueue = random.choice(
                self.nextQueueList
            )
            if not selectedNextQueue.isFull():
                # # tempArrivalTime = int(random.expovariate(selectedNextQueue.customerEventSim.arrivalRate))
                tempCustomerEvent = customerEvent
                tempCustomerEvent.CustomerStatus = CustomerStatus.ARRIVAL
                selectedNextQueue.customerEventSim.addCustomerEvent(tempCustomerEvent)
                
                # print(self.totalWaitingTime,'\n')
                # print("\nCustomer depart queue ", self.name, " to queue ", selectedNextQueue.name, " at ", self.currentTime)
                # print("TotalWaitingTime: ", self.totalWaitingTime,'\n')
                # self.stats()
                # self.show_each()
                # selectedNextQueue.customerEventSim.numGenerate(customerNum=1, arrivalTime=self.currentTime)
        # print("\nCustomer depart queue ", self.name)

    def isFull(self):
        return self.waitingQueue.full()

    def run(self, simulationTime):
        while self.queueStatus != QueueStatus.STOP:
            if (not self.customerEventSim.eventList and simulationTime <= self.currentTime and not self.waitCustomerFromOtherQueue):
                self.stop()
                if self.nextQueueList:
                    self.notifyOtherQueue()
                            
            if self.customerEventSim.eventList:
                with self.lock:
                    event = self.customerEventSim.eventList.pop(0)
                #totalWaitingTime = total time wait in system 
                '''
                    current time - previous time = service time 
                    servingNum = #customer waiting for service & served
                    Capacity = 15, k = 5
                    waiting queue = 10 = CONST 
                    
                '''
                self.totalWaitingTime += (self.currentTime - self.previousTime) * (
                     self.waitingQueue.qsize()
                )
                
                # print(self.totalWaitingTime,'\n')
                
                self.totalQueueTime += (
                    self.currentTime - self.previousTime
                ) * self.waitingQueue.qsize()
                self.previousTime = self.currentTime
                self.currentTime = event.arrivalTime
                if event.CustomerStatus == CustomerStatus.DEPART:
                    self.depart(event)
                elif event.CustomerStatus == CustomerStatus.ARRIVAL:
                    self.arrival(event)
                # print('\n--queueName=', self.name, 'waitingQueueSize=', self.waitingQueue.qsize(), 'servingNum=', self.servingNum)

    def stop(self):
        self.queueStatus = QueueStatus.STOP
        
        
    # Notify other queue if stop    
    def notifyOtherQueue(self):
        for queue in self.nextQueueList:
            queue.waitCustomerFromOtherQueue = False

    def stats(self):
        try:
            self.avgWaitLen = self.totalWaitingTime / self.currentTime  # Corrected variable name
            self.avgWaitQuLen = self.totalQueueTime / self.currentTime
            self.avgWaitTime = self.totalWaitingTime / self.totalServedCustomers
            self.avgWaitQuTime = self.totalQueueTime / self.totalServedCustomers
        except ZeroDivisionError:
            print("ZeroDivisionError")
        
    def show_each(self):
        
        print("-------------------------------------------------")
        print("queueName=",self.name, "\nstats:")
        print("avgWaitTime=", self.avgWaitTime)
        print('awgWaitLen=', self.avgWaitLen)
        print('avgWaitQuTime=', self.avgWaitQuTime)
        print('avgWaitQuLen=', self.avgWaitQuLen)
        print('totalServedCustomers=', self.totalServedCustomers)
        print("-------------------------------------------------")
