from time import sleep
from datetime import datetime
from .Mongo import *
from .Drone import Drone
from .Model import Model
from shapely.geometry import LineString, Polygon
from .util import is_inside_polygon
import math

def drone_cleaning(drone:Drone, model:Model, exit_event):
    # add initial angle code to pickup initial angle from mongo
    initial_angle = drone.yaw
    traversal_slope = math.tan(math.radians(initial_angle))

    points = []
    for coordinate in drone.area:
        points.append((coordinate['lon'], coordinate['lat']))
    polygon = Polygon(points)

    flag = False
    lat_a, lon_a, lat_b, lon_b = find_lowest_points(drone=drone)
    line = create_line(x=lon_a, y=lat_a, slope=traversal_slope) 
    intersection = line.intersection(polygon)
    if len(intersection.coords) != 1:
        print("Not Lowest Point")
        flag = True
    else:
        min_lat = lat_a

    if flag == True:
        line = create_line(x=lon_b, y=lat_b, slope=traversal_slope)
        intersection = line.intersection(polygon)
        if len(intersection.coords) != 1:
            print("Not Lowest Point, wrong points selected.")
        else:
            min_lat = lat_b
        
    max_lat = find_highest_point(drone=drone)
    
    # Creating waypoints for drone movement
    left = []
    right = []
    array_dist = 2          # input array_dist from software in meters
    array_dist = array_dist / 111300        # in arc
    vertical_dist = array_dist * math.cos(math.radians(initial_angle))

    possible_lat = min_lat
    while possible_lat <= max_lat:
        if flag == True:
            line = create_line(x=lon_b, y=possible_lat, slope=traversal_slope)
        else:
            line = create_line(x=lon_a, y=possible_lat, slope=traversal_slope)

        intersection = line.intersection(polygon)
        if len(intersection.coords) != 2:
            print("Invalid.")
        else:
            left.append(intersection.coords[0])
            right.append(intersection.coords[1])
        possible_lat += vertical_dist

    # MOVEMENT STARTS HERE
    target_height = 2
    drone.takeoff_drone(target_height)
    
    level = 0
    direction, next_loc = find_closest_point(drone, left=left, right=right, level=level)
    drone.goto_location(next_loc[1], next_loc[0], 2)
    print("On the Location")

    count = 0
    while True:
        if level > len(left):
            print('Inpection Finished')
            # Drone RTL and Land with exit_event
            break
        drone.update_drone()
        if count < 15 and is_inside_polygon(points=points, p=(drone.lon, drone.lat)):
            panel_status = center_with_panel(drone=drone, model=model, level=level)
            if panel_status == 'No Panel':
                count += 1
            else:
                count = 0
                # MOVE DRONE DOWN TOWARDS PANEL
            if direction == True:
                # MOVE RIGHT FOR 1 SEC
                print("Right")
                drone.move_right(time=1)
            else:
                # MOVE LEFT FOR 1 SEC
                print("Left")
                drone.move_left(time=1)
        else:
            level += 1
            count = 0
            direction, next_loc = find_closest_point(drone=drone, left=left, right=right, level=level)
            model.panel_num=[0, direction]
            drone.goto_location(next_loc[1], next_loc[0], 2)

def drone_clean_drop(drone:Drone, model:Model, exit_event, drone_collection, rover_collection):
    # update_drone_status(drone=drone, drone_collection=drone_collection, status="Drop")
    print("Received Command to drop a rover")
    print(drone.target_point_lat)
    print(drone.target_point_lon)
    drone.takeoff_drone(2)
    print("add mission somehow (brainstorm later)")

    print("Navigate to 1st wp")
    sleep(1)
    print("Centering with panel")
    # centerWithPanel(drone,drone_collection,exit_event)
    sleep(1)
    print("Landing slowly as long as coordinates dont change. If coordinates change recenter with panel, else keep landing")
    # same coordinates algo
    print("Landed")
    print("Setting Drone Status to Dropped")
    # drone.droneStatus="Dropped"
    update_drone_status(drone=drone, drone_collection=drone_collection, status="Dropped")
    update_rover_status(drone=drone, rover_collection=rover_collection, status="UnDock")

    # sleep(3)
    # print("Received Command from rover to go back to home location")
    # # Go back
    # print("Update database that this drone is now free")
    return
    
def drone_clean_pickup(drone:Drone, model:Model, exit_event, drone_collection, rover_collection):
    # update_drone_status(drone=drone, drone_collection=drone_collection, status="Pickup")
    print("Command to pick up a rover")
    drone.takeoff_drone(2)
    print("Check location of rover to pick from mongo")
    print("Navigate to that location")
    print("Centering with panel")
    sleep(1)
    print("Landing slowly as long as coordinates dont change. If coordinates change recenter with panel, else keep landing")
    print("Landed")
    update_drone_status(drone=drone, drone_collection=drone_collection, status="Dock")
    update_rover_status(drone=drone, rover_collection=rover_collection, status="Dock")
    print("Sending command to mongo to start rover parking")
    sleep(3)
    # print("Received Command from rover to go to a location(home/next panel)")
    # print("if Next Panel repeat above function to drop rover")
    # print("Else RTL and notify database")
    return

def go_to_home(drone:Drone, drone_collection, rover_collection, exit_event):
    print("Going back to Home")
    drone.takeoff_drone(2)

    serial = drone.serial
    for i in range(10):
        sleep(1)
    print("Back Home")
    print("Landing")
    sleep(5)
    print("Landed Drone")
    print("Set drone and rover status to free")
    update_drone_status(drone=drone, drone_collection=drone_collection, status="Free")
    update_rover_status(drone=drone, rover_collection=rover_collection, status="Free")

def wait_at_home(drone:Drone, drone_collection, exit_event):
    print("Going back to Home")
    drone.takeoff_drone(2)

    serial=drone.serial
    for i in range(10):
        sleep(1)
    print("Back Home")
    print("Landing")
    sleep(5)
    print("Landed Drone")
    update_drone_status(drone=drone, drone_collection=drone_collection, status="Wait")
   
# Run inference on current frame and center to the panel
def center_with_panel(drone:Drone, model:Model, level):
    while True:
        if drone.is_model_free:
            # add promise and callback
            move_command = model.detect_panel(drone, drone.camera.image)
            print("Move Command Found", move_command)
            if(move_command == "Right"):
                print("Move Right")
                drone.move_right(time=1, speed=0.1)
                
            elif move_command == "Left":
                print("Move Left")
                drone.move_left(time=1, speed=0.1)
                
            elif move_command == "Forward":
                print("Move Forward")
                drone.move_forward(time=1, speed=0.1)
                
            elif move_command == "Backward":
                print("Move Backward")
                drone.move_backward(time=1, speed=0.1)
                
            elif move_command == "Centered":
                print("Centered")
                return "Centered"
            
            elif move_command == "No Panel":
                print("continue with explicit commands")
                return "No Panel"
            
            else:
                print("No Frame Found")
                sleep(1)
        else:
            sleep(0.2)

# Find closest point to the drone
def find_closest_point(drone:Drone, left, right, level):
    drone.update_drone()
    left_dist = math.sqrt((drone.lat - left[level][1])**2 + (drone.lon - left[level][0])**2)
    right_dist = math.sqrt((drone.lat - right[level][1])**2 + (drone.lon - right[level][0])**2)
    
    if left_dist < right_dist:
        return True, left[level]
    else:
        return False, right[level]
    
# Find 2 lowest points according to latitude
def find_lowest_points(drone:Drone):    
    lat_a = drone.area[0]['lat']
    lon_a = drone.area[0]['lon']
    lat_b = drone.area[0]['lat']
    lon_b = drone.area[0]['lon']

    for iter in range(1, len(drone.area)):
        if drone.area[iter]['lat'] < lat_a:
            lat_b = lat_a
            lon_b = lon_a
            lat_a = drone.area[iter]['lat']
            lon_a = drone.area[iter]['lon']
        elif drone.area[iter]['lat'] < lat_b and drone.area[iter]['lat'] != lat_a:
            lat_b = drone.area[iter]['lat']
            lon_b = drone.area[iter]['lon']

    return lat_a, lon_a, lat_b, lon_b

# Find highest points according to latitude
def find_highest_point(drone:Drone):
    max_lat = drone.area[0]['lat']
    for iter in range(1, len(drone.area)):
        if max_lat < drone.area[iter]['lat']:
            max_lat = drone.area[iter]['lat']

    return max_lat

# Create a line that goes through given point
def create_line(x, y, slope):
    line_x = [x - 10, x + 10]
    line_y = [y + (slope * (possible_x - x)) for possible_x in line_x]
    line = LineString([(line_x[0], line_y[0]), (line_x[1], line_y[1])])
    
    return line

if __name__ == "__main__":
    pass