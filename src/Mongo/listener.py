import time
from threading import Event, Thread

from ..util import keyboard_shutdown
from .setup import mongoUpdateDroneBySerial

def listenerMongoData(drone,dataCollection,exit_event):
    print("Mongo Listner Started")
    serial=drone.serial

    pipeline = [{
        '$match': {
            '$and': [
                {"updateDescription.updatedFields.takeOffStatus": {'$exists': True}},
                {'operationType': "update"}]
        }
    }]
    
    try:
        for document in dataCollection.watch(pipeline=pipeline, full_document='updateLookup'):
            if document['fullDocument']['serial'] == serial:
                
                updated_takeOffStatus = document['fullDocument']['takeOffStatus']
                #inspection_area = createInspectionArea(document=document)                
                droneSerial = document['fullDocument']['serial']

                #print(inspection_area)

                if updated_takeOffStatus == True and droneSerial == serial:
                    print("------------------Take off---------------------")

                    ##------> START CLEANING ALGO

                    # drone.area=inspection_area
                    # t = Thread(target=droneSurvey,
                    #            args=(drone,exit_event))
                    # t.start()

                elif updated_takeOffStatus == False and droneSerial == serial:
                    print("-------------------Land------------------------")
                    print("-> Start Landing Process")

                    ##------> LAND THE DRONE

                    # vehicle land function from drone class
                    # drone.landDrone()
                    # exit_event.set()
                    # print("-> Exit Event Set")
                    # t.join()
                    

    except KeyboardInterrupt:
        keyboard_shutdown()

def listenerMoveCommand(drone,dataCollection):
    print("Listening to Movement")
    serial=drone.serial

    pipeline = [{
        '$match': {
            '$and': [
                {"updateDescription.updatedFields.move": {'$exists': True}},
                {'operationType': "update"}]
        }
    }]

    try:
        for document in dataCollection.watch(pipeline=pipeline, full_document='updateLookup'):
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


def updateDroneData(dataCollection,drone):
    try:
        while True:
            print("Updating Drone")
            mongoUpdateDroneBySerial(drone,dataCollection)
            print(drone.serial)
            time.sleep(5)
    except KeyboardInterrupt:
        keyboard_shutdown()
