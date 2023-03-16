from pymavlink import mavutil
from time import sleep
import math
from ..Camera import Camera

class Drone:
    def __init__(self, drone_serial, connection):
        vehicle = mavutil.mavlink_connection(connection)
        vehicle.wait_heartbeat()
        print("Heartbeat from system (system %u component %u)" % (vehicle.target_system, vehicle.target_component))

        _ = vehicle.messages.keys() #All parameters that can be fetched
        
        pos = vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        attitude = self.vehicle.recv_match(type='ATTITUDE', blocking=True)
        self.update_drone()

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
        self.change_vehicle_mode("LAND")
        sleep(1)

    def send_local_ned_velocity(self, vx, vy, vz):
        self.vehicle.mav.send(mavutil.mavlink.MAVLink_set_position_target_local_ned_message(10, self.vehicle.target_system,
                                                                                            self.vehicle.target_component, 
                                                                                            mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, 
                                                                                            int(0b110111000111), 
                                                                                            0, 0, 0, vx, vy, vz, 0, 0, 0, 0, 0))
        
    # def send_local_ned_velocity(self, vx, vy, vz):
    #     msg = self.vehicle.message_factory.set_position_target_local_ned_encode(0, 0, 0, 
    #                                                                             mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,
    #                                                                             0b0000111111000111,
    #                                                                             0, 0, 0, vx, vy, vz, 0, 0, 0, 0, 0)
    #     self.vehicle.send_mavlink(msg)
    #     self.vehicle.flush()

    def goto_location(self, lat, lon, alt):
        print("Go To Location")
        self.update_drone()
        self.vehicle.mav.send(mavutil.mavlink.MAVLink_set_position_target_global_int_message(10, self.vehicle.target_system, 
                                                                                             self.vehicle.target_component, 
                                                                                             mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                                                                             int(0b110111111000),
                                                                                             int(lat*10**7),
                                                                                             int(lon*10**7),
                                                                                             2, 0, 0, 0, 0, 0, 0, 0, 0))
        sleep(1)
        print("Go To Command")
        sleep(1)
        
        # msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True)
        # print(msg)
        
        sleep(1)
        print("Go To Acknowledge")
        sleep(1)
        # print(self.lat, lat)
        # print(self.lon, lon)
        while((abs(self.lat - lat) >= 0.000001) and (abs(self.lon - lon) >= 0.000001)):
            sleep(1)
            msg = self.vehicle.recv_match(type='NAV_CONTROLLER_OUTPUT', blocking=True)
            # print(self.lat, lat)
            # print(self.lon, lon)
            # print(self.alt)
            self.update_drone()
            self.vehicle.mav.send(mavutil.mavlink.MAVLink_set_position_target_global_int_message(10, self.vehicle.target_system,
                                                                                                 self.vehicle.target_component,
                                                                                                 mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                                                                                 int(0b110111111000),
                                                                                                 int(lat*10**7),
                                                                                                 int(lon*10**7),
                                                                                                 alt, 0, 0, 0, 0, 0, 0, 0, 0))
            # sleep(1)
            # print("Goto Command")
            # sleep(1)

            # msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True)
            print(msg)
            print("-+-+-+-+--+-+-+-+--+-+-+-+--+-+-+-+--+-+-+-+--+-+-+-+-")
        return

    def move_forward(self, time=2, speed=0.5):
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
            counter += 1

if __name__== "__main__":
    pass

