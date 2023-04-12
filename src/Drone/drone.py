from pymavlink import mavutil
from enum import Enum
from time import sleep
import math
from ..Camera import Camera
from . import droneFunctions


class RoverStatus(Enum):
    FREE = 1
    INIT = 2
    DOCK = 3
    UNDOCK = 4
    BUSY = 5
    CLEANING = 6
    PICKUP = 7

class DroneStatus(Enum):
    FREE = 1
    INIT = 2
    WAIT_AT_HOME = 3
    GO_HOME = 4
    NEXT_PANEL=5
    DOCK = 6
    PICKUP = 7
    DROP = 8
    DROPPED = 9
    WAITING=10

class Drone:
    def __init__(self, drone_serial, connection):
        vehicle = mavutil.mavlink_connection(connection)
        vehicle.wait_heartbeat()
        print("Heartbeat from system (system %u component %u)" % (vehicle.target_system, vehicle.target_component))

        _ = vehicle.messages.keys() #All parameters that can be fetched
        
        pos = vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        attitude = vehicle.recv_match(type='ATTITUDE', blocking=True)
        self.serial = drone_serial
        self.area={}
        self.socket_ip = ""
        self.socket_port = 5656
        self.vehicle = vehicle
        self.takeoff_status = False
        self.target_point_lat = pos.lat * 10e-8
        self.target_point_lon = pos.lon * 10e-8
        self.rover_serial = "ERROR000000000"
        self.drone_status = "Free"
        self.rover_status = "Free"
        self.user_id = ''
        self.camera = Camera()
        self.is_model_free = True
        self.yaw = math.degrees(attitude.yaw)
        self.update_drone()


    def change_vehicle_mode(self, mode):
        print("Changing vehicle mode to", mode)
        # Get mode ID
        mode_id = self.vehicle.mode_mapping()[mode]
        # Set new mode

        self.vehicle.mav.set_mode_send(self.vehicle.target_system, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode_id)
        msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True)
        print(msg)

    def update_drone(self):
        pos = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        system = self.vehicle.recv_match(type='SYS_STATUS', blocking=True)
        self.battery = system.battery_remaining
        self.alt = pos.relative_alt * 10e-3
        self.lat = pos.lat * 10e-8
        self.lon = pos.lon * 10e-8

    def takeoff_drone(self, height):
        self.takeoff_status = True
        self.change_vehicle_mode("GUIDED")
        
        self.vehicle.mav.command_long_send(self.vehicle.target_system, self.vehicle.target_component, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
        msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True)
        print(msg)

        self.vehicle.mav.command_long_send(self.vehicle.target_system, self.vehicle.target_component, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, height)
        msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True)
        print(msg)

        self.update_drone()
        while (self.alt <= 0.9*(height)):
            self.update_drone()
            msg = self.vehicle.recv_match(type='NAV_CONTROLLER_OUTPUT', blocking=True)
            print(msg)
            sleep(1)
            print("Taking off")

        sleep(3)
        print("Takeoff Complete")

    def land_drone(self):
        self.takeoff_status = False
        print("landing...")        
        self.changeVehicleMode("LAND")
        time.sleep(1)

    def sendLocalNedVelocity(self, vx, vy, vz):
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,
            0, 0,
            mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,
            0b0000111111000111,
            0, 0, 0,
            vx, vy, vz,
            0, 0, 0,
            0, 0)
        self.vehicle.send_mavlink(msg)
        self.vehicle.flush()

    def moveForward(self, time=2, speed=0.5):
        counter = 0
        while counter < time:
            self.send_local_ned_velocity(speed, 0, 0)
            sleep(1)
            print('forward')
            counter += 1

    def move_backward(self, time=2, speed=0.5):
        counter = 0
        while counter < time:
            self.send_local_ned_velocity(-speed, 0, 0)
            sleep(1)
            print('backward')
            counter += 1

    def move_right(self, time=2, speed=0.5):
        counter = 0
        while counter < time:
            self.send_local_ned_velocity(0, speed, 0)
            sleep(1)
            print('right')
            counter += 1

    def move_left(self, time=2, speed=0.5):
        counter = 0
        while counter < time:
            self.send_local_ned_velocity(0, -speed, 0)
            sleep(1)
            print('left')
            counter = counter+1

    def handle_drone_status(self,statusValue,droneDataCollection,roverDataCollection,exit_event):
            print(statusValue)
            statusKey=""
            for status in DroneStatus:
                if status.value == statusValue:
                    statusKey= status
                    break
            print(statusValue,statusKey)

            if statusKey == DroneStatus.FREE:
                self.droneStatus=statusKey
                droneFunctions.free(drone=self)
            elif statusKey == DroneStatus.INIT:
                self.droneStatus=statusKey
                droneFunctions.init(drone=self,roverDataCollection=roverDataCollection,RoverStatus=RoverStatus)
            elif statusKey == DroneStatus.WAIT_AT_HOME:
                self.droneStatus=statusKey
                droneFunctions.waitAtHome(drone=self,droneDataCollection=droneDataCollection,DroneStatus=DroneStatus,exit_event=exit_event)
            elif statusKey == DroneStatus.GO_HOME:
                self.droneStatus=statusKey
                droneFunctions.goHome(drone=self,roverDataCollection=roverDataCollection,droneDataCollection=droneDataCollection,DroneStatus=DroneStatus,RoverStatus=RoverStatus,exit_event=exit_event)
            elif statusKey == DroneStatus.NEXT_PANEL:
                self.droneStatus=statusKey
                droneFunctions.nextPanel(drone=self,roverDataCollection=roverDataCollection,droneDataCollection=droneDataCollection,DroneStatus=DroneStatus,RoverStatus=RoverStatus,exit_event=exit_event)
            elif statusKey == DroneStatus.DOCK:
                self.droneStatus=statusKey
                droneFunctions.dock
            elif statusKey == DroneStatus.PICKUP:
                self.droneStatus=statusKey
                droneFunctions.pickup(drone=self,droneDataCollection=droneDataCollection,roverDataCollection=roverDataCollection,DroneStatus=DroneStatus,RoverStatus=RoverStatus,exit_event=exit_event)
            elif statusKey == DroneStatus.DROP:
                self.droneStatus=statusKey
                droneFunctions.drop(drone=self,droneDataCollection=droneDataCollection,roverDataCollection=roverDataCollection,DroneStatus=DroneStatus,RoverStatus=RoverStatus,exit_event=exit_event)
            elif statusKey == DroneStatus.DROPPED:
                self.droneStatus=statusKey
                droneFunctions.dropped
            elif statusKey == DroneStatus.WAITING:
                self.droneStatus=statusKey
                droneFunctions.waiting
            else:
                print("Invalid status")
            # action()


if __name__== "__main__":
    pass

