import pymongo


# Connect Mongo
def mongoConnect(mongoUrl,database,collection):
    mc = pymongo.MongoClient(mongoUrl)
    mydb = mc[database]
    droneDataCollection = mydb[collection]
    return droneDataCollection

def mongoConnectDroneBySerial(drone,droneDataCollection):
    droneData= droneDataCollection.find_one({'serial': drone.serial})
    if droneData:
        drone.roverSerial=droneData['roverSerial']
        mongoUpdateDroneBySerial(drone=drone,droneDataCollection=droneDataCollection)
    else:
        mongoInsertDrone(drone=drone,droneDataCollection=droneDataCollection)
    
def mongoUpdateDroneBySerial(drone,droneDataCollection):
    droneDataCollection.update_one({'serial': drone.serial}, {'$set': {'battery': drone.battery, 'location': {
            'lat': drone.lat, 'lon': drone.lon}}})
    print('DRONE UPDATED')

def mongoInsertDrone(drone,droneDataCollection):
    droneDataCollection.insert_one({'serial': drone.serial, 'battery': drone.battery, 'location': {
            'lat': drone.lat, 'lon': drone.lon}, 'takeOffStatus': False, 'userId': None, 'droneStatus':"Free"})
    print('DRONE ADDED')

def mongoUpdateDroneStatus(drone,droneDataCollection,status):
    droneDataCollection.update_one({'serial': drone.serial}, {'$set': {'droneStatus': status}})
    drone.droneStatus=status
    print('DRONE STATUS UPDATED')


def mongoUpdateRoverStatus(drone,roverDataCollection,status):
    roverDataCollection.update_one({'serial': drone.roverSerial}, {'$set': {'droneStatus': status}})
    drone.roverStatus=status
    print('DRONE STATUS UPDATED')    


# def mongoGetRoverStatus(drone,roverDataCollection):
#     roverDocument=roverDataCollection.find_one({'serial': drone.roverSerial})
#     roverStatus=roverDocument['roverStatus']
#     drone.roverStatus=roverStatus
#     print('ROVER STATUS UPDATED')

# def mongoUpdateDroneTakeoffStatus(drone,droneDataCollection,takeoffStatus):
    # droneDataCollection.update_one({'serial': drone.serial}, {'$set': {'takeoffStatus': takeoffStatus}})
    # drone.takeoffStatus=takeoffStatus
    # print('Takeoff Status UPDATED')