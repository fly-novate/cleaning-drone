import time
from threading import Event, Thread
from ..util import keyboard_shutdown,createInspectionArea
from .setup import mongoUpdateDroneBySerial
from ..drone_clean import droneCleanDrop,droneCleanPickup,goToHome,waitAtHome
from datetime import datetime

def listenerMongoData(drone,droneDataCollection,roverDataCollection,exit_event):
    print("Mongo Listner Started")
    serial=drone.serial

    pipelineTakeOff = [{
        '$match': {
            '$and': [
                {"updateDescription.updatedFields.takeOffStatus": {'$exists': True}},
                {'operationType': "update"}]
        }
    }]


    pipelineDroneStatus = [{
        '$match': {
            '$and': [
                {"updateDescription.updatedFields.droneStatus": {'$exists': True}},
                {'operationType': "update"}]
        }
    }]
    
    try:
        for document in droneDataCollection.watch(pipeline=pipelineDroneStatus, full_document='updateLookup'):
            if document['fullDocument']['serial'] == serial:
                
                # updated_takeOffStatus = document['fullDocument']['takeOffStatus']
                updated_droneStatus = document['fullDocument']['droneStatus']
                droneSerial = document['fullDocument']['serial']
                print("Change in drone status")
                print(updated_droneStatus)

                # if(document['fullDocument']['droneStatus']=="Free"):
                    # print("Edge case, Deal later")
                    
                if droneSerial == serial:
                    # if(mongoRoverStatus(drone=drone,roverDataCollection=roverDataCollection)=="Free"):
                    # if((drone.droneStatus=="Free") and updated_droneStatus=="Drop"):
                    if(updated_droneStatus=="Drop"):
                        drone.droneStatus='Drop'
                        print("Drop")
                        print("------------------Drop Rover---------------------")
                        t = Thread(target=droneCleanDrop,
                                args=(drone,exit_event,droneDataCollection,roverDataCollection))
                        # t = Thread(target=droneCleanDrop,
                        #        args=(drone,exit_event,droneDataCollection,roverDataCollection=roverDataCollection))
                        t.start()

                    elif(updated_droneStatus=="Pickup"):
                        print("Pickup")
                        print("------------------Pick Rover---------------------")
                        t = Thread(target=droneCleanPickup,
                                   args=(drone,exit_event,droneDataCollection,roverDataCollection))
                        t.start()
                   
                    elif(updated_droneStatus=="goHome"):
                        print("------------------Going Back to Home------------------")
                        t = Thread(target=goToHome,
                                   args=(drone,droneDataCollection,roverDataCollection,exit_event))
                        t.start()

                    elif(updated_droneStatus=="waitAtHome"):
                        print("------------------Going Back to Home to wait------------------")
                        t = Thread(target=waitAtHome,
                                   args=(drone,droneDataCollection,exit_event))
                        t.start()
                    
                    elif(updated_droneStatus=="nextPanel"):
                        print("------------------Going to next panel------------------")
                        t = Thread(target=droneCleanDrop,
                                args=(drone,exit_event,droneDataCollection,roverDataCollection))
                        # t = Thread(target=droneCleanDrop,
                        #        args=(drone,exit_event,droneDataCollection,roverDataCollection=roverDataCollection))
                        t.start()
                        # t = Thread(target=nextPanel,
                        #            args=(drone,exit_event,droneDataCollection))
                        # t.start()

                    
                    else:
                        pass
                    

                # elif updated_takeOffStatus == False and droneSerial == serial:
                #     print("-------------------Land------------------------")
                #     print("-> Start Landing Process")

                #     ##------> LAND THE DRONE

                #     # vehicle land function from drone class
                #     # drone.landDrone()
                #     # exit_event.set()
                #     # print("-> Exit Event Set")
                #     # t.join()
                #     pass
                    

    except KeyboardInterrupt:
        keyboard_shutdown()


def listenerMoveCommand(drone,droneDataCollection):
    print("Listening to Movement")
    serial=drone.serial

    pipelineMoveCommand = [{
        '$match': {
            '$and': [
                {"updateDescription.updatedFields.move": {'$exists': True}},
                {'operationType': "update"}]
        }
    }]

    try:
        for document in droneDataCollection.watch(pipeline=pipelineMoveCommand, full_document='updateLookup'):
            if document['fullDocument']['serial'] == serial:
                
                movementDirection = document['fullDocument']['move']
                droneSerial = document['fullDocument']['serial']

                if movementDirection == 'Stop' and droneSerial == serial:
                    print('Stopping')

                elif movementDirection == 'Forward' and droneSerial == serial:
                    print('Forward')

                elif movementDirection == 'Backward' and droneSerial == serial:
                    print('Backward')
                
                elif movementDirection == 'Right' and droneSerial == serial:
                    print('Right')

                elif movementDirection == 'Left' and droneSerial == serial:
                    print('Left')
                    
                    

    except KeyboardInterrupt:
        keyboard_shutdown()


def updateDroneData(droneDataCollection,drone):
    try:
        while True:
            print("Updating Drone")
            mongoUpdateDroneBySerial(drone,droneDataCollection)
            print(drone.serial)
            time.sleep(5)
    except KeyboardInterrupt:
        keyboard_shutdown()
