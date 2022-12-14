'''
Gripper Class intended to work with the summer reinforcement learning package being developed
by the University of Auckland Robotics Lab

Beth Cutler
'''
import numpy as np
import dynamixel_sdk as dxl
import time
from gripperFunctions import Servo

# TODO figure out how the fiducal marker is gonna work


class Gripper9(object):
    def __init__(self):

        # is it best practice to do these as class variables? or do I just make them variables that get intialised in the __init__ function?
        self.num_motors = 9
        self.motor_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.motor_positions = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.baudrate = 57600
        self.devicename = "COM5"  # need to change if in linux, will be dependent on the system
        self.protocol = 2.0  # XL-320 uses protocol 2
        self.addresses = {
            "torque_enable": 24,
            "torque_limit": 35,
            "led": 25,
            "goal_position": 30,
            "present_position": 37,
            "present_velocity": 38,
            "moving_speed": 32,
            "moving": 49
        }
        self.torque_limit = 180

        self.port_handler = dxl.PortHandler(self.devicename)
        self.packet_handler = dxl.PacketHandler(self.protocol)

        self.group_sync_write = dxl.GroupSyncWrite(
            self.port_handler, self.packet_handler, self.addresses["goal_position"], 2)
        self.group_sync_read = dxl.GroupSyncRead(
            self.port_handler, self.packet_handler, self.addresses["present_position"], 2)

        # create nine servo instances
        self.servo1 = Servo(
            self.port_handler, self.packet_handler, 0, self.addresses, 1)
        self.servo2 = Servo(
            self.port_handler, self.packet_handler, 3, self.addresses, 2)
        self.servo3 = Servo(
            self.port_handler, self.packet_handler, 2, self.addresses, 3)
        self.servo4 = Servo(
            self.port_handler, self.packet_handler, 0, self.addresses, 4)
        self.servo5 = Servo(
            self.port_handler, self.packet_handler, 7, self.addresses, 5)
        self.servo6 = Servo(
            self.port_handler, self.packet_handler, 5, self.addresses, 6)
        self.servo7 = Servo(
            self.port_handler, self.packet_handler, 0, self.addresses, 7)
        self.servo8 = Servo(
            self.port_handler, self.packet_handler, 4, self.addresses, 8)
        self.servo9 = Servo(
            self.port_handler, self.packet_handler, 6, self.addresses, 9)

        # combine all servo instances
        self.servos = [self.servo1, self.servo2, self.servo3, self.servo4,
                       self.servo5, self.servo6, self.servo7, self.servo8, self.servo9]

    def setup(self):

        # open port, set baudrate
        if self.port_handler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            quit()
        # set port baudrate
        if self.port_handler.setBaudRate(self.baudrate):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            quit()

        # setup certain specs of the servos
        for servo in self.servos:
            servo.limit_torque()
            servo.limit_speed()
            servo.enable_torque()
            servo.turn_on_LED()

    """ actions is an array of joint positions that specifiy the desired position of each servo"""

    def move(self, action):

        # TODO potientially add a check in here that clips the actions given from the network just to set some kind of limit
        # TODO make sure there are enough joint positions in the actions array

        # loop through the actions array and send the commands to the motors

        
            for servo in self.servos:
                # add parameters to the groupSyncWrite
                self.group_sync_write.addParam(servo.motor_id, [
                    dxl.DXL_LOBYTE(action[servo.motor_id-1]), dxl.DXL_HIBYTE(action[servo.motor_id-1])])

            # transmit the packet
            dxl_comm_result = self.group_sync_write.txPacket()
            if dxl_comm_result == dxl.COMM_SUCCESS:
                print("group_sync_write Succeeded")

            self.group_sync_write.clearParam()

            # using moving flag to check if the motors have reached their goal position
            while self.gripper_moving_check():
                self.all_current_positions()
        # check for errors/got to position before moving on (IS THERE A FLAG???)

    def all_current_positions(self):

        # TODO see if there is a just a rx packet function that can be used here
        self.group_sync_read.txRxPacket()

        for servo in self.servos:
            self.group_sync_read.addParam(servo.motor_id)
        for servo in self.servos:
            currentPos = self.group_sync_read.getData(
                servo.motor_id, self.addresses["present_position"], 2)
            self.motor_positions[servo.motor_id -
                                 1] = np.round(((0.2929 * currentPos) - 150), 1)
        print(self.motor_positions)

        return self.motor_positions

    def gripper_moving_check(self):
        moving = False
        for servo in self.servos:
            moving |= servo.moving_check()
        return moving

    def close(self):
        # disable torque
        for servo in self.servos:
            servo.disable_torque()
        # close port
        self.port_handler.closePort()
