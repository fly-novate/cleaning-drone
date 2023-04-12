from datetime import datetime
import socket, pickle, imutils, struct, cv2
# from ..Drone import Drone

class Camera:
    def __init__(self):
        self.image = []
        self.camera = cv2.VideoCapture(0)

    def send_camera_frames(self, drone, collection):
        print("hey")
        # host_name="ec2-43-205-129-4.ap-south-1.compute.amazonaws.com"
        # host_name="localhost"

        # host_ip=socket.gethostbyname(host_name)
        # print(host_ip)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("waiting for socket connection")
        # serial = "ERROR000000000"
        serial = drone.serial
        if collection.find({'serial': serial}): 
            drone_data = collection.find({'serial': serial})
            host_ip = drone_data[0]['socketIP']
            # host_ip="3.110.220.25"
            # host_ip="3.109.133.16"
            # host_name="ec2-43-205-129-4.ap-south-1.compute.amazonaws.com"
            # host_ip=socket.gethostbyname(host_name)
            port = drone_data[0]['socketPort']
            print(host_ip, port)
        # client_socket.connect((host_ip, port))

        # #host_ip = '192.168.9.116'
        # #port = 5656
        # client_socket.connect((host_ip, port))

        window_name = "Video Stream"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        while True:
            # Read Frame and process
            ret, frame = self.camera.read()
            # frame = cv2.resize(frame, (320, 240))
            # print(frame)
            self.image = frame
            socket_frame = imutils.resize(frame, width=360, height=360)
            msg=[]
            # msgTime=datetime.now()
            # msgTime = datetime.now() # time object
            msg.append(socket_frame)
            # msg.append(msgTime)
            # socketFrame=frame
            a = pickle.dumps(socket_frame)
            msg_frame = struct.pack("Q", len(a)) + a

            try:
                client_socket.sendall(msg_frame)
                print("after sendall")
            except:
                print('Error')
                pass
            
            cv2.imshow(window_name, socket_frame)

            key = cv2.waitKey(1)
            if key == ord("q"):
                break

        cv2.destroyWindow(window_name)

if __name__ == "__main__":
    # send_camera_frames()
    pass