"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = 1
NORTH = 0

NCARS = 100
NPED = 10
TIME_CARS_NORTH = 0.5  # a new car enters each 0.5s
TIME_CARS_SOUTH = 0.5  # a new car enters each 0.5s
TIME_PED = 5 # a new pedestrian enters each 5s
TIME_IN_BRIDGE_CARS = (1, 0.5) # normal 1s, 0.5s
TIME_IN_BRIDGE_PEDESTRIAN = (30,10) # normal 1s, 0.5s

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        
        self.ncars_0 = Value('i', 0)
        self.ncarsWaiting_0 = Value('i',0)
        
        self.ncars_1 = Value('i', 0)
        self.ncarsWaiting_1 = Value('i',0)
        
        self.npedestrians = Value('i',0)
        self.npedWaiting = Value('i',0)
        
        self.turn = Value('i',0)

        self.can_pedestrians = Condition(self.mutex)
        self.can_cars_0 = Condition(self.mutex)
        self.can_cars_1 = Condition(self.mutex)

    def canEnter_carsN(self):
       # print(f'condicion carsN: {self} turno: {self.turn.value} == 0 ')

        return ((self.npedestrians.value == 0 and \
            (self.turn.value != 2 or self.npedWaiting.value == 0)) and \
            (self.ncars_1.value == 0 and \
                (self.turn.value != 1 or self.ncarsWaiting_1.value == 0)))
  
    def canEnter_carsS(self):
       # print(f'condicion carsS: {self} turno: {self.turn.value} == 1')
        return ((self.npedestrians.value == 0 and \
            (self.turn.value != 2 or self.npedWaiting.value == 0)) and \
                (self.ncars_0.value == 0 and \
            (self.turn.value != 0 or self.ncarsWaiting_0.value == 0)))
    
    def canEnter_ped(self):
       # print(f'condicion ped: {self} turno: {self.turn.value} == 2')
        return ((self.ncars_1.value == 0 and \
            (self.turn.value != 1 or self.ncarsWaiting_1.value == 0)) and \
                (self.ncars_0.value == 0 and \
            (self.turn.value != 0 or self.ncarsWaiting_0.value == 0)))
    
    
    def wants_enter_car(self, direction: int) -> None:
        self.mutex.acquire()
        
        if direction == 0:
            self.ncarsWaiting_0.value += 1
            self.can_cars_0.wait_for(self.canEnter_carsN)
            self.ncarsWaiting_0.value -= 1
            self.ncars_0.value += 1

        else:
            self.ncarsWaiting_1.value += 1
            self.can_cars_1.wait_for(self.canEnter_carsS)
            self.ncarsWaiting_1.value -= 1
            self.ncars_1.value += 1
            
       # print(f' Puede pasar coche dirección {direction}, {self}')

            
        self.mutex.release()

    def leaves_car(self, direction: int) -> None:
        self.mutex.acquire() 
        if direction == 0:
            self.ncars_0.value -= 1
            
            if self.ncarsWaiting_1.value > 0:
                self.turn.value = 1
            elif self.npedWaiting.value > 0:
                self.turn.value = 2
                
            if self.ncars_0.value == 0:
                #self.turn.value = 1
                self.can_cars_1.notify_all()
                self.can_pedestrians.notify_all()
            
        else:
            self.ncars_1.value -= 1
            
            if self.npedWaiting.value > 0:
                self.turn.value = 2
            elif self.ncarsWaiting_0.value > 0:
                self.turn.value = 0
            
                
            if self.ncars_1.value == 0:
                #self.turn.value = 2
                self.can_pedestrians.notify_all() 
                self.can_cars_0.notify_all()
            
        self.mutex.release()

    def wants_enter_pedestrian(self) -> None:
        self.mutex.acquire()
        self.npedWaiting.value += 1
        #print('Peatón espera a ver si entra')
        self.can_pedestrians.wait_for(self.canEnter_ped)
        self.npedWaiting.value -= 1
        self.npedestrians.value += 1      
        self.mutex.release()
        #print('Peatón puede pasar')

    def leaves_pedestrian(self) -> None:
        self.mutex.acquire()
        self.npedestrians.value -= 1

        if self.ncarsWaiting_0.value > 0:
            self.turn.value = 0
        elif self.ncarsWaiting_1.value > 0:
            self.turn.value = 1
        
        if self.npedestrians.value == 0:
            #self.turn.value = 0
            self.can_cars_0.notify_all()
            self.can_cars_1.notify_all()
            
        self.mutex.release()

    def __repr__(self) -> str:
        #return (f'M <p:{self.npedestrians.value}, p_W:{self.npedWaiting.value},'
               # f' cN:{self.ncars_0.value}, cN_W:{self.ncarsWaiting_0.value},'
    #f' cS:{self.ncars_1.value}, cS_W:{self.ncarsWaiting_1.value}>')
    
        return f'M <p:{self.npedestrians.value}, cN:{self.ncars_0.value}, cS:{self.ncars_1.value}>'


def delay_car_north() -> None:
    time.sleep(random.choice(TIME_IN_BRIDGE_CARS))

def delay_car_south() -> None:
    time.sleep(random.choice(TIME_IN_BRIDGE_CARS))

def delay_pedestrian() -> None:
    time.sleep(random.choice(TIME_IN_BRIDGE_PEDESTRIAN))


def car(cid: int, direction: int, monitor: Monitor)  -> None:
    print(f"car {cid} heading {direction} wants to enter. {monitor}")
    monitor.wants_enter_car(direction)
    print(f"car {cid} heading {direction} enters the bridge. {monitor}")
    if direction==NORTH :
        delay_car_north()
    else:
        delay_car_south()
    print(f"car {cid} heading {direction} leaving the bridge. {monitor}")
    monitor.leaves_car(direction)
    print(f"car {cid} heading {direction} out of the bridge. {monitor}\n")

def pedestrian(pid: int, monitor: Monitor) -> None:
    print(f"pedestrian {pid} wants to enter. {monitor}")
    monitor.wants_enter_pedestrian()
    print(f"pedestrian {pid} enters the bridge. {monitor}")
    delay_pedestrian()
    print(f"pedestrian {pid} leaving the bridge. {monitor}")
    monitor.leaves_pedestrian()
    print(f"pedestrian {pid} out of the bridge. {monitor} \n")



def gen_pedestrian(monitor: Monitor) -> None:
    pid = 0
    plst = []
    for _ in range(NPED):
        pid += 1
        p = Process(target=pedestrian, args=(pid, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/TIME_PED))

    for p in plst:
        p.join()

def gen_cars(direction: int, time_cars, monitor: Monitor) -> None:
    cid = 0
    plst = []
    for _ in range(NCARS):
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/time_cars))

    for p in plst:
        p.join()

def main():
    monitor = Monitor()
    gcars_north = Process(target=gen_cars, args=(NORTH, TIME_CARS_NORTH, monitor))
    gcars_south = Process(target=gen_cars, args=(SOUTH, TIME_CARS_SOUTH, monitor))
    gped = Process(target=gen_pedestrian, args=(monitor,))
    gcars_north.start()
    gcars_south.start()
    gped.start()
    gcars_north.join()
    gcars_south.join()
    gped.join()


if __name__ == '__main__':
    main()
