from pymavlink import mavutil
import argparse  
parser = argparse.ArgumentParser()
parser.add_argument('--connect', default='127.0.0.1:14550')
args = parser.parse_args()

print ('Connecting to vehicle on: %s' % args.connect)
the_connection = mavutil.mavlink_connection(args.connect)

the_connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" %
      (the_connection.target_system, the_connection.target_component))

while 1:
      # msg = the_connection.recv_match(type='ATTITUDE', blocking=True)
      pos = the_connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)

      # distance to next waypoint
      msg = the_connection.recv_match(type='NAV_CONTROLLER_OUTPUT',blocking=True)

      print(msg)