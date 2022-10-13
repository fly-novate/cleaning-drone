import argparse
import src.Mongo as Mongo
import src.settings as settings
import src.start as start


def main():
    url = settings.MONGODB_ATLAS_URL
    db = settings.DATABASE
    col = settings.COLLECTION
    dataCollection = Mongo.mongoConnect(mongoUrl=url,database=db,collection=col)

    serial = settings.getserial()
    parser = argparse.ArgumentParser()
    parser.add_argument('--connect', default='127.0.0.1:14550')
    args = parser.parse_args()

    print ('Connecting to vehicle on: %s' % args.connect)
    start.mainStart(serial=serial, connection = args.connect,dataCollection=dataCollection)

if __name__ == '__main__':
    main()