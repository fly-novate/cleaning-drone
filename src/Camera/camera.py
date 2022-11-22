import pymongo
import pickle
import imutils
from imutils.video import VideoStream
import socket
import cv2
import time
import struct

MONGODB_ATLAS_URL = "mongodb+srv://Neshtek:pAiqGS3uFqBtzSX2@flynovate-website.bqwpz.mongodb.net/database?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"

DATABASE = "database"

COLLECTION = "drones"

mc = pymongo.MongoClient(MONGODB_ATLAS_URL)
mydb = mc[DATABASE]
mycol = mydb[COLLECTION]



def sendCameraFrames():
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
        # host_ip = droneData[0]['socketIP']
        host_ip="3.110.220.25"
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
        print(frame)
        socketFrame=imutils.resize(frame,width=360,height=360)
        # socketFrame=frame
        a=pickle.dumps(socketFrame)
        message = struct.pack("Q", len(a))+a
        try:
            client_socket.sendall(message)
            print("after sendall")
        except:
            print('Error')
            pass
        
        # cv2.waitKey(0) # waits until a key is pressed
        cv2.imshow(window_name,socketFrame)

        key = cv2.waitKey(1)
        if key == ord("q"):
            break

    cv2.destroyWindow(window_name)


    

    # Create a context structure responsible for managing all connected USB cameras.
    # Cameras with other IO types can be managed by using a bitwise or of the
    # SeekCameraIOType enum cases.
    # with SeekCameraManager(SeekCameraIOType.USB) as manager:
    #     # Start listening for events.
    #     renderer = Renderer()
    #     manager.register_event_callback(on_event, renderer)

    #     while True:
    #         # Wait a maximum of 150ms for each frame to be received.
    #         # A condition variable is used to synchronize the access to the renderer;
    #         # it will be notified by the user defined frame available callback thread.
    #         with renderer.frame_condition:
    #             if renderer.frame_condition.wait(150.0 / 1000.0):
    #                 img = renderer.frame.data

    #                 # Resize the rendering window.
    #                 if renderer.first_frame:
    #                     (height, width, _) = img.shape
    #                     cv2.resizeWindow(window_name, width * 2, height * 2)
    #                     renderer.first_frame = False

    #                 # Render the image to the window.
                  
                    
    #                 socketFrame=imutils.resize(img,width=360)
    #                 a=pickle.dumps(img)
    #                 message = struct.pack("Q", len(a))+a
    #                 try:
    #                     client_socket.sendall(message)
    #                     print("after sendall")
    #                 except:
    #                     print('Error')
    #                     pass
    #                 cv2.imshow(window_name, img)
                    

    #         # Process key events.
    #         key = cv2.waitKey(1)
    #         if key == ord("q"):
    #             break

    #         # Check if the window has been closed manually.
    #         if not cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):
    #             break

    cv2.destroyWindow(window_name)

# def sendCameraFrames():
#     while(1):
#         print("camera running")
#         time.sleep(5)

if __name__ == "__main__":
    sendCameraFrames()

