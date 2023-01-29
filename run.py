import argparse
import src.Mongo as Mongo
import src.settings as settings
import src.start as start


def main():
    url = settings.MONGODB_ATLAS_URL
    db = settings.DATABASE
    droneCol = settings.DRONE_COLLECTION
    roverCol = settings.ROVER_COLLECTION


    droneDataCollection = Mongo.mongoConnect(mongoUrl=url,database=db,collection=droneCol)
    roverDataCollection = Mongo.mongoConnect(mongoUrl=url,database=db,collection=roverCol)

    serial = settings.getserial()
    parser = argparse.ArgumentParser()
    parser.add_argument('--connect', default='127.0.0.1:14550')
    args = parser.parse_args()

    print ('Connecting to vehicle on: %s' % args.connect)
    start.mainStart(serial=serial, connection = args.connect,droneDataCollection=droneDataCollection,roverDataCollection=roverDataCollection)

if __name__ == '__main__':
    main()