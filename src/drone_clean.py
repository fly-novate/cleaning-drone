import time
def droneCleanDrop(drone,exit_event):
    print("Received Command to drop a rover")
    print(drone.targetPointLat)
    print(drone.targetPointLon)
    targetHeight=2
    print("Takeoff Drone")
    print("add mission somehow (brainstorm later)")
    drone.takeoffDrone(targetHeight)
    pos = drone.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)

    while (pos.relative_alt*1e-3 <= 0.9*(targetHeight)):
        pos = drone.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        msg = drone.vehicle.recv_match(type='NAV_CONTROLLER_OUTPUT',blocking=True)
        time.sleep(1)
    
    print("Navigate to 1st wp")
    time.sleep(1)
    print("Centering with panel")
    time.sleep(1)
    print("Landing slowly as long as coordinates dont change. If coordinates change recenter with panel, else keep landing")

    print("Landed")
    print("Sending command to mongo to start rover")
    time.sleep(3)
    print("Received Command from rover to go back to home location")
    print("Update database that this drone is now free")
    


def droneCleanPickup(drone):
    print("Command to pick up a rover")
    targetHeight=2
    print("Takeoff Drone")
    drone.takeoffDrone(targetHeight)
    pos = drone.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)

    while (pos.relative_alt*1e-3 <= 0.9*(targetHeight)):
        pos = drone.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        msg = drone.vehicle.recv_match(type='NAV_CONTROLLER_OUTPUT',blocking=True)
        time.sleep(1)
    print("Check location of rover to pick from mongo")
    print("Navigate to that location")
    print("Centering with panel")
    time.sleep(1)
    print("Landing slowly as long as coordinates dont change. If coordinates change recenter with panel, else keep landing")
    print("Landed")
    print("Sending command to mongo to start rover parking")
    time.sleep(3)
    print("Received Command from rover to go to a location(home/next panel)")
    print("if Next Panel repeat above function to drop rover")
    print("Else RTL and notify database")
   

    