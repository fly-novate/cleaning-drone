import time
from datetime import datetime
from .Mongo import *

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

def droneCleanDrop(drone,exit_event,droneDataCollection,roverDataCollection):
    # mongoUpdateDroneStatus(drone=drone,droneDataCollection=droneDataCollection,status="Drop")
    print("Received Command to drop a rover")
    print(drone.targetPointLat)
    print(drone.targetPointLon)
    takeOffDrone(drone,2)
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
    # drone.droneStatus="Dropped"
    mongoUpdateDroneStatus(drone=drone,droneDataCollection=droneDataCollection,status="Dropped")
    mongoUpdateRoverStatus(drone=drone,roverDataCollection=roverDataCollection,status="UnDock")


    # time.sleep(3)
    # print("Received Command from rover to go back to home location")
    # # Go back
    # print("Update database that this drone is now free")
    return
    

def droneCleanPickup(drone,exit_event,droneDataCollection,roverDataCollection):
    # mongoUpdateDroneStatus(drone=drone,droneDataCollection=droneDataCollection,status="Pickup")
    print("Command to pick up a rover")
    takeOffDrone(drone,2)
    print("Check location of rover to pick from mongo")
    print("Navigate to that location")
    print("Centering with panel")
    time.sleep(1)
    print("Landing slowly as long as coordinates dont change. If coordinates change recenter with panel, else keep landing")
    print("Landed")
    mongoUpdateDroneStatus(drone=drone,droneDataCollection=droneDataCollection,status="Dock")
    mongoUpdateRoverStatus(drone=drone,roverDataCollection=roverDataCollection,status="Dock")
    print("Sending command to mongo to start rover parking")
    time.sleep(3)
    # print("Received Command from rover to go to a location(home/next panel)")
    # print("if Next Panel repeat above function to drop rover")
    # print("Else RTL and notify database")
    return
   

def centerWithPanel(drone,droneDataCollection,exit_event):
    print("Started Center with panel")
    # serial=drone.serial
    serial=drone.serial
    moveDuration=1
    moveSpeed=0.5
    time.sleep(5)
    print("Landed on panel")


#  Remove pipeline and regularly check command even if same
    # pipeline = [{
    #     '$match': {
    #         '$and': [
    #             {"updateDescription.updatedFields.frameTime": {'$exists': True}},
    #             {'operationType': "update"}]
    #     }
    # }]
    # try:
    #     for document in droneDataCollection.watch(pipeline=pipeline, full_document='updateLookup'):
    #         refTime=datetime.now().time()
    #         if document['fullDocument']['serial'] == serial:
                
    #             update_frameTime = document['fullDocument']['frameTime']
    #             # inspection_area = createInspectionArea(document=document)                
    #             droneSerial = document['fullDocument']['serial']
    #             if update_frameTime >= refTime and droneSerial == serial:
    #                 # match the format of timings
    #                 print("------------------Found Command---------------------")
    #                 print(document['fullDocument']['move'])
    #                 print(update_frameTime)

    #                 movementDirection = document['fullDocument']['move']

    #                 if movementDirection == 'Stop' and droneSerial == serial:
    #                     # while relative alt is high enough, move drone down,
    #                     # else land 
    #                     print('Downward')

    #                 elif movementDirection == 'Forward' and droneSerial == serial:
    #                     drone.moveForward(moveDuration,moveSpeed)
    #                     print('Forward')

    #                 elif movementDirection == 'Backward' and droneSerial == serial:
    #                     drone.moveBackward(moveDuration,moveSpeed)
    #                     print('Backward')
                    
    #                 elif movementDirection == 'Right' and droneSerial == serial:
    #                     drone.moveRight(moveDuration,moveSpeed)
    #                     print('Right')

    #                 elif movementDirection == 'Left' and droneSerial == serial:
    #                     drone.moveLeft(moveDuration,moveSpeed)
    #                     print('Left')
    #             else:
    #                 time.sleep(0.5)
    #                 continue
    #             ##------> START CLEANING ALGO

    #                 # t = Thread(target=droneCleanDrop,
    #                 #             args=(drone,exit_event))
    #                 # t.start()

    #                 # print("If Pick up")
    #                 # t = Thread(target=droneCleanPickup,
    #                 #             args=(drone,exit_event))
    #                 # t.start()

    
    # except:
    #     pass
    pass

def goToHome(drone,droneDataCollection,roverDataCollection,exit_event):
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
    mongoUpdateDroneStatus(drone=drone,droneDataCollection=droneDataCollection,status="Free")
    mongoUpdateRoverStatus(drone=drone,roverDataCollection=roverDataCollection,status="Free")

def waitAtHome(drone,droneDataCollection,exit_event):
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
    mongoUpdateDroneStatus(drone=drone,droneDataCollection=droneDataCollection,status="Wait")


if __name__ == "__main__":
    pass