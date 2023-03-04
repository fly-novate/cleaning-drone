from time import sleep
from threading import Thread
from ..util import keyboard_shutdown, create_inspection_area
from .setup import update_drone_by_serial
from ..drone_clean import drone_clean_drop, drone_clean_pickup, go_to_home, wait_at_home
from ..Drone import Drone
from ..Model import Model

def listener_mongo_data(drone:Drone, model:Model, drone_collection, rover_collection, exit_event):
    print("Mongo Listener Started")
    serial=drone.serial

    pipeline_takeoff = [{
        '$match': {
            '$and': [
                {"updateDescription.updatedFields.takeOffStatus": {'$exists': True}},
                {'operationType': "update"}]
        }
    }]

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

                # if(document['fullDocument']['droneStatus'] == "Free"):
                    # print("Edge case, Deal later")
                    
                if drone_serial == serial:
                    # if(mongo_rover_status(drone=drone, rover_collection=rover_collection) == "Free"):
                    # if((drone.drone_status == "Free") and updated_drone_status == "Drop"):
                    if(updated_drone_status == "Drop"):
                        drone.drone_status = 'Drop'
                        # print("Drop")
                        print("------------------Drop Rover---------------------")
                        t = Thread(target=drone_clean_drop, args=(drone, model, exit_event, drone_collection, rover_collection))
                        # t = Thread(target=drone_clean_drop,
                        #        args=(drone,exit_event,drone_collection,rover_collection=rover_collection))
                        t.start()

                    elif(updated_drone_status == "Pickup"):
                        # print("Pickup")
                        print("------------------Pick Rover---------------------")
                        t = Thread(target=drone_clean_pickup, args=(drone, model, exit_event, drone_collection, rover_collection))
                        t.start()
                    
                    elif(updated_drone_status == "goHome"):
                        print("------------------Going Back to Home------------------")
                        t = Thread(target=go_to_home, args=(drone, drone_collection, rover_collection, exit_event))
                        t.start()

                    elif(updated_drone_status == "waitAtHome"):
                        print("------------------Going Back to Home to wait------------------")
                        t = Thread(target=wait_at_home, args=(drone, drone_collection, exit_event))
                        t.start()
                    
                    elif(updated_drone_status == "nextPanel"):
                        print("------------------Going to next panel------------------")
                        t = Thread(target=drone_clean_drop, args=(drone, model, exit_event, drone_collection, rover_collection))
                        # t = Thread(target=drone_clean_drop,
                        #        args=(drone,exit_event,drone_collection,rover_collection=rover_collection))
                        t.start()
                        # t = Thread(target=nextPanel,
                        #            args=(drone,exit_event,drone_collection))
                        # t.start()

                    else:
                        pass

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

def update_drone_data(drone_collection, drone:Drone):
    try:
        while True:
            # print("Updating Drone")
            update_drone_by_serial(drone, drone_collection)
            # print(drone.serial)
            sleep(1)
    except KeyboardInterrupt:
        keyboard_shutdown()

if __name__ == '__main__':
    pass