from threading import Event, Thread
from ..util import keyboard_shutdown
import src.Mongo as Mongo
import time


def free(drone):
    print("Drone is free.")
    return

def init(drone,roverDataCollection,RoverStatus):
    print("Drone is init.")
    takeOffDrone(drone,2)
    Mongo.mongoUpdateRoverStatusBySerial(drone=drone,roverDataCollection=roverDataCollection,status=RoverStatus.INIT)
    return

def drop(drone,droneDataCollection,roverDataCollection,DroneStatus,RoverStatus,exit_event):
    print("Drop")
    print("------------------Drop Rover---------------------")
    t = Thread(target=droneCleanDrop,
            args=(drone,droneDataCollection,roverDataCollection,DroneStatus,RoverStatus,exit_event))
    # t = Thread(target=droneCleanDrop,
    #        args=(drone,exit_event,droneDataCollection,roverDataCollection=roverDataCollection))
    t.start()
    return


def waitAtHome(drone,droneDataCollection,DroneStatus,exit_event):
    print("------------------Going Back to Home to wait------------------")
    t = Thread(target=waitAtHomeMain,
                args=(drone,droneDataCollection,DroneStatus,exit_event))
    t.start()
    return

def goHome(drone,droneDataCollection,roverDataCollection,DroneStatus,RoverStatus,exit_event):
    print("------------------Going Back to Home------------------")
    t = Thread(target=goToHome,
                args=(drone,droneDataCollection,roverDataCollection,DroneStatus,RoverStatus,exit_event))
    t.start()

def nextPanel(drone,droneDataCollection,roverDataCollection,DroneStatus,RoverStatus,exit_event):
    print("------------------Going to next panel------------------")
    t = Thread(target=droneCleanDrop,
            args=(drone,droneDataCollection,roverDataCollection,DroneStatus,RoverStatus,exit_event))
    # t = Thread(target=droneCleanDrop,
    #        args=(drone,exit_event,droneDataCollection,roverDataCollection=roverDataCollection))
    t.start()
    return

def dock(drone):
    print("Drone is dock.")
    return

def pickup(drone,droneDataCollection,roverDataCollection,DroneStatus,RoverStatus,exit_event):
    print("Pickup")
    print("------------------Pick Rover---------------------")
    t = Thread(target=droneCleanPickup,
                args=(drone,droneDataCollection,roverDataCollection,DroneStatus,RoverStatus,exit_event))
    t.start()
    return



def dropped(drone):
    print("Drone is dropped.")
    return

def waiting(drone):
    print("Drone is waiting.")
    return

def takeOffDrone(drone,targetHeight):
    targetHeight=2
    print("Takeoff Drone")
    drone.takeoffDrone(targetHeight)
    pos = drone.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)

    while (pos.relative_alt*1e-3 <= 0.9*(targetHeight)):
        pos = drone.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        msg = drone.vehicle.recv_match(type='NAV_CONTROLLER_OUTPUT',blocking=True)
        time.sleep(1)
    print("Reached Altitude",targetHeight)
    return

def droneCleanDrop(drone,droneDataCollection,roverDataCollection,DroneStatus,RoverStatus,exit_event):
    # mongoUpdateDroneStatus(drone=drone,droneDataCollection=droneDataCollection,status="Drop")
    print("Received Command to drop a rover")
    print(drone.targetPointLat)
    print(drone.targetPointLon)
    # takeOffDrone(drone,2)
    print("add mission somehow (brainstorm later)")

    print("Navigate to 1st wp")
    time.sleep(1)
    print("Centering with panel")
    # centerWithPanel(drone,droneDataCollection,exit_event)
    time.sleep(1)
    print("Landing slowly as long as coordinates dont change. If coordinates change recenter with panel, else keep landing")
    # same coordinates algo
    print("Landed")
    print("Setting Drone Status to Dropped")
    drone.droneStatus=DroneStatus.DROPPED
    Mongo.mongoUpdateDroneBySerial(drone=drone,droneDataCollection=droneDataCollection)
    Mongo.mongoUpdateRoverStatusBySerial(drone=drone,roverDataCollection=roverDataCollection,status=RoverStatus.UNDOCK)


    # time.sleep(3)
    # print("Received Command from rover to go back to home location")
    # # Go back
    # print("Update database that this drone is now free")
    return
    
def droneCleanPickup(drone,droneDataCollection,roverDataCollection,DroneStatus,RoverStatus,exit_event):
    # mongoUpdateDroneStatus(drone=drone,droneDataCollection=droneDataCollection,status="Pickup")
    print("Command to pick up a rover")
    takeOffDrone(drone,2)
    print("Check location of rover to pick from mongo")
    print("Navigate to that location")
    print("Centering with panel")
    time.sleep(1)
    print("Landing slowly as long as coordinates dont change. If coordinates change recenter with panel, else keep landing")
    print("Landed")

    drone.droneStatus=DroneStatus.DOCK
    Mongo.mongoUpdateDroneBySerial(drone=drone,droneDataCollection=droneDataCollection)
    Mongo.mongoUpdateRoverStatusBySerial(drone=drone,roverDataCollection=roverDataCollection,status=RoverStatus.DOCK)

    print("Sending command to mongo to start rover parking")
    time.sleep(3)
    # print("Received Command from rover to go to a location(home/next panel)")
    # print("if Next Panel repeat above function to drop rover")
    # print("Else RTL and notify database")
    return

def goToHome(drone,droneDataCollection,roverDataCollection,DroneStatus,RoverStatus,exit_event):
    print("Going back to Home")
    takeOffDrone(drone,2)

    # serial=drone.serial
    serial=drone.serial
    for i in range(10):
        time.sleep(1)
    print("Back Home")
    print("Landing")
    time.sleep(5)
    print("Landed Drone")
    print("Set drone and rover status to free")
    drone.droneStatus=DroneStatus.FREE
    Mongo.mongoUpdateDroneBySerial(drone=drone,droneDataCollection=droneDataCollection)
    Mongo.mongoUpdateRoverStatusBySerial(drone=drone,roverDataCollection=roverDataCollection,status=RoverStatus.FREE)

def waitAtHomeMain(drone,droneDataCollection,DroneStatus,exit_event):
    print("Going back to Home")
    takeOffDrone(drone,2)
    # serial=drone.serial
    serial=drone.serial
    for i in range(10):
        time.sleep(1)
    print("Back Home")
    print("Landing")
    time.sleep(5)
    print("Landed Drone")
    drone.droneStatus=DroneStatus.WAITING
    Mongo.mongoUpdateDroneBySerial(drone=drone,droneDataCollection=droneDataCollection)

def centerWithPanel(drone,droneDataCollection,exit_event):
    print("Started Center with panel")
    # serial=drone.serial
    serial=drone.serial
    moveDuration=1
    moveSpeed=0.5
    time.sleep(5)
    print("Landed on panel")