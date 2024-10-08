from pymavlink import mavutil
import time

class Drone:
    def __init__(self,droneSerial,connection):
        vehicle = mavutil.mavlink_connection(connection)
        vehicle.wait_heartbeat()
        print("Heartbeat from system (system %u component %u)" % (vehicle.target_system, vehicle.target_component))

        _ = vehicle.messages.keys() #All parameters that can be fetched
        
        pos = vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        system = vehicle.recv_match(type='SYS_STATUS', blocking=True)
        
        self.serial=droneSerial
        self.alt=pos.relative_alt * 10e-3
        self.lat=pos.lat * 10e-8
        self.lon=pos.lon * 10e-8
        self.battery=system.battery_remaining
        self.area=[]
        self.socketIP=""
        self.socketPort=5656
        self.vehicle=vehicle
        self.takeoffStatus=False
        self.targetPointLat=pos.lat * 10e-8
        self.targetPointLon=pos.lon * 10e-8
        self.roverSerial="ERROR000000000"
        self.droneStatus="Free"
        self.roverStatus="Free"

    def changeVehicleMode(self,mode):
        print("Changing vehicle mode to",mode)
        # Get mode ID
        mode_id = self.vehicle.mode_mapping()[mode]
        # Set new mode

        self.vehicle.mav.set_mode_send(
            self.vehicle.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id)
        msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True)
        print(msg)

    def takeoffDrone(self,height):
        self.takeoffStatus=True
        self.changeVehicleMode("GUIDED")
        print(self.vehicle)
        self.vehicle.mav.command_long_send(self.vehicle.target_system, self.vehicle.target_component,
                                            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
        msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True)
        print(msg)

        self.vehicle.mav.command_long_send(self.vehicle.target_system, self.vehicle.target_component,
                                            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, height)

        msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True)
        print(msg)
        return

    def landDrone(self):
        self.takeoffStatus=False
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
            self.sendLocalNedVelocity(speed, 0, 0)
            time.sleep(1)
            print('forward')
            counter = counter+1

    def moveBackward(self, time=2, speed=0.5):
        counter = 0
        while counter < time:
            self.sendLocalNedVelocity(-speed, 0, 0)
            time.sleep(1)
            print('backward')
            counter = counter+1

    def moveRight(self, time=2, speed=0.5):
        counter = 0
        while counter < time:
            self.sendLocalNedVelocity(0, speed, 0)
            time.sleep(1)
            print('right')
            counter = counter+1

    def moveLeft(self, time=2, speed=0.5):
        counter = 0
        while counter < time:
            self.sendLocalNedVelocity(0, -speed, 0)
            time.sleep(1)
            print('left')
            counter = counter+1


if __name__== "__main__":
    pass

