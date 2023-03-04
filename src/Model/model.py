import torch
import cv2
from ..Drone import Drone

class Model:
    def __init__(self):
        panel_detector_path = 'src/Model/weights/best.pt'
        torch.hub._validate_not_a_forked_repo = lambda a, b, c: True
        detector = torch.hub.load('ultralytics/yolov5', 'custom', path=panel_detector_path, force_reload=True)
        
        self.detector = detector
        self.result = []
        self.labels = []
        self.coord = []
        self.closest_coord = []
        self.box_center = []

    # image preprocessing for yoloV5
    def preprocess(self, image):
        # print(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (640,640))
        return image

    # labels and coordinates of bounding box
    def split_result(self):
        self.labels = self.result.xyxyn[0][:, -1].to('cpu').numpy()
        self.coord = self.result.xyxyn[0][:, :-1].to('cpu').numpy()

    # calculate coordinates in pixel values
    def find_coordinates(self, image, coord):
        x_shape, y_shape = image.shape[1], image.shape[0]
        x1 = int(coord[0] * x_shape)
        y1 = int(coord[1] * y_shape)
        x2 = int(coord[2] * x_shape)
        y2 = int(coord[3] * y_shape)

        coordinates = [x1, y1, x2, y2]
        return coordinates 
    
    # calculate area of bounding box
    def calculate_area(self, image, coord):
        coordinates = self.find_coordinates(image, coord)
        area = (coordinates[2] - coordinates[0]) * (coordinates[1] - coordinates[3])
        abs_area = abs(area)
        return int(abs_area)

    # determine closest panel to the drone
    def find_closest_panel(self, image):
        bb_areas = []
        if len(self.labels) > 1:
            for i in range(len(self.labels)):
                bb_areas.append(self.calculate_area(image, self.coord[i]))
            max_area = bb_areas[0]
            pos = 0
            for i in range(len(bb_areas)):
                if bb_areas[i] > max_area:
                        max_area = bb_areas[i]
                        pos = i
        else:
            pos = 0

        # drawing bounding box on closest panel
        self.closest_coord = self.find_coordinates(image, self.coord[pos])
        # cv2.rectangle(image, (self.closest_coord[0], self.closest_coord[1]), (self.closest_coord[2], self.closest_coord[3]), (0, 255, 255), 2)

    # marking centers of camera feed and detected panel
    def mark_centers(self, image):
        center_box_x = int((self.closest_coord[0] + self.closest_coord[2]) / 2)
        center_box_y = int((self.closest_coord[1] + self.closest_coord[3]) / 2)
        # cv2.circle(image, (320, 240), 3, (255, 0, 0), 2)                            # center of image = blue
        # cv2.circle(image, (center_box_x, center_box_y), 3, (0, 255, 0), 2)          # center of bounding box = green
        
        self.box_center = [center_box_x, center_box_y]

    # panel inspection using custom trained YOLOv5 model
    def detect_panel(self, drone:Drone, image):
        drone.is_model_free = False
        if image == []:
            print('No Frame')
            drone.is_model_free = True
            return 'No Frame'
        
        preprocessed_image = self.preprocess(image)
        self.result = self.detector(preprocessed_image)
        self.split_result()

        if self.labels.any():                                          # panel detection check 
            self.find_closest_panel(image)
            self.mark_centers(image)

            # checking x-axis alignment within error range of 25px
            if (self.box_center[0] - 320) > 25:
                print("Right")
                drone.is_model_free = True
                return "Right"
            if (self.box_center[0] - 320) < -25:
                print("Left")
                drone.is_model_free = True
                return "Left"

            # x-axis alignment means y-axis needs to be aligned now
            if (self.box_center[0] - 320) < 25 and (self.box_center[0] - 320) > -25:
                print("Centered along X-Axis")

                # checking y-axis alignment within error range of 25px
                if (self.box_center[1] - 240) > 25:
                    print('Forward')
                    drone.is_model_free = True
                    return "Forward"
                if (self.box_center[1] - 240) < -25:
                    print('Backward')
                    drone.is_model_free = True
                    return "Backward"

                # x-axis and y-axis alignment successful means Photo needs to be taken
                if (self.box_center[1] - 240) < 25 and (self.box_center[1] - 240) > -25:
                    print('Centered')
                    drone.is_model_free = True
                    return "Centered"
        
        else:
            print('No Panels')
            drone.is_model_free = True
            return 'No Panel'

if __name__ == '__main__':
    pass