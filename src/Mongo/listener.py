import time
from threading import Event, Thread
from ..util import keyboard_shutdown,createInspectionArea
from .setup import update_drone_by_serial
# from ..drone_clean import droneCleanDrop,droneCleanPickup,goToHome,waitAtHome
from datetime import datetime

def listenerMongoData(drone,drone_collection,roverDataCollection,exit_event):
    print("Mongo Listner Started")
    serial=drone.serial


    pipeline_drone_status = [{
        '$match': {
            '$and': [
                {"updateDescription.updatedFields.droneStatus": {'$exists': True}},
                {'operationType': "update"}]
        }
    }]
    
    try:
        for document in drone_collection.watch(pipeline=pipeline_drone_status, full_document='updateLookup'):
            if document['fullDocument']['serial'] == serial:
                
                # updated_takeOffStatus = document['fullDocument']['takeOffStatus']
                updated_drone_status = document['fullDocument']['droneStatus']
                drone_serial = document['fullDocument']['serial']
                print("Change in drone status")
                print(updated_drone_status)
                if drone_serial == serial:
                    drone.handle_drone_status(updated_drone_status,drone_collection,roverDataCollection,exit_event)


                # if(document['fullDocument']['droneStatus'] == "Free"):
                    # print("Edge case, Deal later")
                    
                # if droneSerial == serial:
                #     # if(mongoRoverStatus(drone=drone,roverDataCollection=roverDataCollection)=="Free"):
                #     # if((drone.droneStatus=="Free") and updated_droneStatus=="Drop"):
                #     if(updated_droneStatus=="Drop"):
                #         drone.droneStatus='Drop'
                #         print("Drop")
                #         print("------------------Drop Rover---------------------")
                #         t = Thread(target=droneCleanDrop,
                #                 args=(drone,exit_event,drone_collection,roverDataCollection))
                #         # t = Thread(target=droneCleanDrop,
                #         #        args=(drone,exit_event,drone_collection,roverDataCollection=roverDataCollection))
                #         t.start()

                #     elif(updated_droneStatus=="Pickup"):
                #         print("Pickup")
                #         print("------------------Pick Rover---------------------")
                #         t = Thread(target=droneCleanPickup,
                #                    args=(drone,exit_event,drone_collection,roverDataCollection))
                #         t.start()
                   
                #     elif(updated_droneStatus=="goHome"):
                #         print("------------------Going Back to Home------------------")
                #         t = Thread(target=goToHome,
                #                    args=(drone,drone_collection,roverDataCollection,exit_event))
                #         t.start()

                #     elif(updated_droneStatus=="waitAtHome"):
                #         print("------------------Going Back to Home to wait------------------")
                #         t = Thread(target=waitAtHome,
                #                    args=(drone,drone_collection,exit_event))
                #         t.start()
                    
                #     elif(updated_droneStatus=="nextPanel"):
                #         print("------------------Going to next panel------------------")
                #         t = Thread(target=droneCleanDrop,
                #                 args=(drone,exit_event,drone_collection,roverDataCollection))
                #         # t = Thread(target=droneCleanDrop,
                #         #        args=(drone,exit_event,drone_collection,roverDataCollection=roverDataCollection))
                #         t.start()
                #         # t = Thread(target=nextPanel,
                #         #            args=(drone,exit_event,drone_collection))
                #         # t.start()

                    
                    # else:
                    #     pass
                    

                # elif updated_takeOffStatus == False and drone_serial == serial:
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

# def listener_move_command(drone:Drone, drone_collection):
#     print("Listening to Movement")
#     serial=drone.serial

#     pipeline_move_command = [{
#         '$match': {
#             '$and': [
#                 {"updateDescription.updatedFields.move": {'$exists': True}},
#                 {'operationType': "update"}]
#         }
#     }]

#     try:
#         for document in drone_collection.watch(pipeline=pipeline_move_command, full_document='updateLookup'):
#             if document['fullDocument']['serial'] == serial:
#                 movement_direction = document['fullDocument']['move']
#                 drone_serial = document['fullDocument']['serial']

#                 if movement_direction == 'Stop' and drone_serial == serial:
#                     print('Stopping')

#                 elif movement_direction == 'Forward' and drone_serial == serial:
#                     print('Forward')

#                 elif movement_direction == 'Backward' and drone_serial == serial:
#                     print('Backward')
                
#                 elif movement_direction == 'Right' and drone_serial == serial:
#                     print('Right')

#                 elif movement_direction == 'Left' and drone_serial == serial:
#                     print('Left')
                    
#     except KeyboardInterrupt:
#         keyboard_shutdown()

def update_drone_data(drone_collection, drone):
    try:
        while True:
            # print("Updating Drone")
            update_drone_by_serial(drone, drone_collection)
            # print(drone.serial)
            time.sleep(1)
    except KeyboardInterrupt:
        keyboard_shutdown()

if __name__ == '__main__':
    pass
