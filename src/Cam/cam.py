from pymavlink import mavutil
import time
import pymongo
import pickle
import imutils
from imutils.video import VideoStream
import socket
import cv2
import time
import struct
from datetime import datetime
import os
from os.path import join, dirname
from dotenv import load_dotenv

def sendCameraFrames():
    MONGODB_ATLAS_URL = "mongodb+srv://Neshtek:pAiqGS3uFqBtzSX2@flynovate-website.bqwpz.mongodb.net/database?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"

    DATABASE = "database"
    droneDataCollection = "drones"
    dotenv_path = join(dirname(__file__), '../','.env')
    load_dotenv(dotenv_path)

    # MONGODB_ATLAS_URL = os.getenv('MONGODB_ATLAS_URL')
    # DATABASE = os.getenv('DATABASE')
    # droneDataCollection = os.getenv('DRONE_COLLECTION')
    # MONGODB_ATLAS_URL = os.getenv('MONGODB_ATLAS_URL')
    # DATABASE = os.getenv('DATABASE')
    # droneDataCollection = os.getenv('DRONE_COLLECTION')
    
    print(MONGODB_ATLAS_URL,DATABASE,droneDataCollection)

    mc = pymongo.MongoClient(MONGODB_ATLAS_URL)
    mydb = mc[DATABASE]
    mycol = mydb[droneDataCollection]

    print("hey")
    # host_name="ec2-43-205-129-4.ap-south-1.compute.amazonaws.com"
    # host_name="localhost"

    # host_ip=socket.gethostbyname(host_name)
    # print(host_ip)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("waiting for socket connection")
    serial="ERROR000000000"
    if mycol.find({'serial': serial}): 
        droneData = mycol.find({'serial': serial})
        host_ip = droneData[0]['socketIP']
        # host_ip="3.110.220.25"
        # host_ip="3.109.133.16"
        # host_name="ec2-43-205-129-4.ap-south-1.compute.amazonaws.com"
        # host_ip=socket.gethostbyname(host_name)
        port = droneData[0]['socketPort']
        print(host_ip,port)
    client_socket.connect((host_ip, port))
    # vs = VideoStream(usePiCamera=False).start()
    vs = cv2.VideoCapture(0)


    # #host_ip = '192.168.9.116'
    # #port = 5656
    # client_socket.connect((host_ip, port))

    
    window_name = "Video Stream"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        # Read Frame and process
        ret,frame = vs.read()
        # frame = cv2.resize(frame, (320, 240))
        # print(frame)
        socketFrame=imutils.resize(frame,width=360,height=360)
        msg=[]
        msgTime=datetime.now()
        msgTime = datetime.now() # time object
        msg.append(socketFrame)
        msg.append(msgTime)
        # socketFrame=frame
        a=pickle.dumps(msg)
        msgFrame = struct.pack("Q", len(a))+a

        try:
            client_socket.sendall(msgFrame)
            # print("after sendall")
        except:
            print('Error')
            pass
        
        # cv2.waitKey(0) # waits until a key is pressed
        cv2.imshow(window_name,socketFrame)

        key = cv2.waitKey(1)
        if key == ord("q"):
            break

    cv2.destroyWindow(window_name)


    


if __name__== "__main__":
    sendCameraFrames()
    # pass

