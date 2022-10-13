import pymongo


# Connect Mongo
def mongoConnect(mongoUrl,database,collection):
    mc = pymongo.MongoClient(mongoUrl)
    mydb = mc[database]
    dataCollection = mydb[collection]
    return dataCollection


def mongoConnectDroneBySerial(drone,dataCollection):
    if dataCollection.find_one({'serial': drone.serial}):
        mongoUpdateDroneBySerial(drone=drone,dataCollection=dataCollection)
    else:
        mongoInsertDrone(drone=drone,dataCollection=dataCollection)
    
def mongoUpdateDroneBySerial(drone,dataCollection):
    dataCollection.update_one({'serial': drone.serial}, {'$set': {'battery': drone.battery, 'location': {
            'lat': drone.lat, 'lon': drone.lon}}})
    print('DRONE UPDATED')

def mongoInsertDrone(drone,dataCollection):
    dataCollection.insert_one({'serial': drone.serial, 'battery': drone.battery, 'location': {
            'lat': drone.lat, 'lon': drone.lon}, 'takeOffStatus': False, 'userId': None})
    print('DRONE ADDED')

