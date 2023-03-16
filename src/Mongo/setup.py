import pymongo
from ..Drone import Drone

# Connect Mongo
def mongo_connect(mongo_url, database, collection):
    mc = pymongo.MongoClient(mongo_url)
    mydb = mc[database]
    drone_collection = mydb[collection]
    return drone_collection

def connect_drone_by_serial(drone:Drone, drone_collection):
    drone_data = drone_collection.find_one({'serial': drone.serial})
    if drone_data:
        drone.rover_serial = drone_data['roverSerial']
        update_drone_by_serial(drone=drone, drone_collection=drone_collection)
    else:
        insert_drone(drone=drone, drone_collection=drone_collection)
    
def update_drone_by_serial(drone:Drone, drone_collection):
    drone.update_drone()
    drone_collection.update_one({'serial': drone.serial}, {'$set': {'battery': drone.battery, 'location': {'lat': drone.lat, 'lon': drone.lon}, 'yaw': drone.yaw}})
    print('DRONE UPDATED')

def insert_drone(drone:Drone, drone_collection):
    drone.update_drone()
    drone_collection.insert_one({'serial': drone.serial, 'battery': drone.battery, 'location': {'lat': drone.lat, 'lon': drone.lon}, 'yaw': drone.yaw, 'takeOffStatus': False, 'userId': None, 'droneStatus':"Free"})
    print('DRONE ADDED')

def update_drone_status(drone:Drone, drone_collection, status):
    drone_collection.update_one({'serial': drone.serial}, {'$set': {'droneStatus': status}})
    drone.drone_status=status
    print('DRONE STATUS UPDATED')

def update_rover_status(drone:Drone, rover_collection, status):
    rover_collection.update_one({'serial': drone.rover_serial}, {'$set': {'roverStatus': status}})
    drone.rover_status=status
    print('ROVER STATUS UPDATED')    

# def get_rover_status(drone:Drone, rover_collection):
#     rover_document = rover_collection.find_one({'serial': drone.rover_serial})
#     rover_status = rover_document['roverStatus']
#     drone.rover_status = rover_status
#     print('ROVER STATUS UPDATED')

# def update_drone_takeoff_status(drone:Drone, drone_collection, takeoff_status):
#     drone_collection.update_one({'serial': drone.serial}, {'$set': {'takeoffStatus': takeoff_status}})
#     drone.takeoff_status = takeoff_status
#     print('Takeoff Status UPDATED')

def find_user(drone:Drone, collection):
    data = collection.find_one({'serial': drone.serial})
    for key, val in data.items():
        if 'userId' in key:
            drone.user_id = val

if __name__ == '__main__':
    pass