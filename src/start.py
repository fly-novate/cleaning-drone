import asyncio
from threading import Event, Thread
from time import sleep
from .Drone import Drone
from .Model import Model
from .Mongo import *
from .Camera import *

def init_drone_on_mongo(drone:Drone, drone_collection):
    connect_drone_by_serial(drone=drone, drone_collection=drone_collection)

def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def data_streams(drone:Drone, model:Model, drone_collection, rover_collection):
    print('Starting Listening to MongoDB.\n')
    exit_event = Event()

    update_loop = asyncio.new_event_loop()
    update_loop.call_soon_threadsafe(listener_mongo_data, drone, drone_collection, rover_collection, exit_event)
    t = Thread(target=start_loop, args=(update_loop,))
    t.start()
    sleep(0.25)

    drone_data_loop = asyncio.new_event_loop()
    drone_data_loop.call_soon_threadsafe(update_drone_data, drone_collection, drone)
    t = Thread(target=start_loop, args=(drone_data_loop,))
    t.start()
    sleep(0.25)

    # move_loop = asyncio.new_event_loop()
    # move_loop.call_soon_threadsafe(Mongo.listenerMoveCommand,drone,droneDataCollection)
    # t = Thread(target=start_loop, args=(move_loop,))
    # t.start()
    # time.sleep(0.25)

    ##----> ADD CAMERA THREAD

    camera_loop = asyncio.new_event_loop()
    camera_loop.call_soon_threadsafe(drone.camera.send_camera_frames, drone, drone_collection)
    t = Thread(target=start_loop, args=(camera_loop,))
    t.start()
    sleep(0.25)


def main_start(serial=None, connection=None, drone_collection=None, rover_collection=None):
    if serial != None:
        print(serial)
        drone = Drone(drone_serial=serial, connection=connection)
        print(drone)

        find_user(drone=drone, collection=drone_collection)
        model = Model()
        print(model)

        # Initialise Drone Data on Mongo
        init_drone_on_mongo(drone=drone, drone_collection=drone_collection)
        data_streams(drone=drone, model=model,drone_collection=drone_collection, rover_collection=rover_collection)

if __name__ == '__main__':
    pass
else:
    main_start()