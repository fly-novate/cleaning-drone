import asyncio
from threading import Event, Thread
import time
from .Drone import *
from .Mongo import *
from .Cam import *


def initDroneOnMongo(drone,droneDataCollection):
    mongoConnectDroneBySerial(drone=drone,droneDataCollection=droneDataCollection)

def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def data_streams(drone,droneDataCollection,roverDataCollection):
    print('Starting Listening to MongoDB.\n')
    exit_event = Event()

    update_loop = asyncio.new_event_loop()
    update_loop.call_soon_threadsafe(listenerMongoData,drone,droneDataCollection,roverDataCollection,exit_event)
    t = Thread(target=start_loop, args=(update_loop,))
    t.start()
    time.sleep(0.25)

    drone_data_loop = asyncio.new_event_loop()
    drone_data_loop.call_soon_threadsafe(updateDroneData,droneDataCollection,drone)
    t = Thread(target=start_loop, args=(drone_data_loop,))
    t.start()
    time.sleep(0.25)

    # move_loop = asyncio.new_event_loop()
    # move_loop.call_soon_threadsafe(Mongo.listenerMoveCommand,drone,droneDataCollection)
    # t = Thread(target=start_loop, args=(move_loop,))
    # t.start()
    # time.sleep(0.25)

    ##----> ADD CAMERA THREAD

    camera_loop = asyncio.new_event_loop()
    camera_loop.call_soon_threadsafe(sendCameraFrames)
    t = Thread(target=start_loop, args=(camera_loop,))
    t.start()
    time.sleep(0.25)


def mainStart(serial=None, connection=None,droneDataCollection=None,roverDataCollection=None):
    if serial != None:
        print(serial)
        drone = Drone(droneSerial=serial, connection=connection)
        print(drone)

        # Initialise Drone Data on Mongo
        initDroneOnMongo(drone=drone,droneDataCollection=droneDataCollection)
        data_streams(drone=drone, droneDataCollection=droneDataCollection,roverDataCollection=roverDataCollection)

if __name__ == '__main__':
    pass
else:
    mainStart()