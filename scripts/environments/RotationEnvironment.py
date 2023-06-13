from environments.Environment import Environment

import logging
import numpy as np
from enum import Enum

from pathlib import Path
file_path = Path(__file__).parent.resolve()

from configurations import EnvironmentConfig, GripperConfig, ObjectConfig

class REWARD_CONSTANTS(Enum):
    MAX_REWARD = 10
    MIN_REWARD =-50

class GOAL_SELECTION_METHOD(Enum):
    FIXED = 0
    RELATIVE = 1
    RELATIVE_90_180_270 = 2

def fixed_goal():
    target_angle = np.random.randint(1, 5)
    if target_angle == 1:
        return 90
    elif target_angle == 2:
        return 180
    elif target_angle == 3:
        return 270
    elif target_angle == 4:
        return 0
    return 90

def fixed_goals(object_current_pose, noise_tolerance):
    current_yaw = object_current_pose

    target_angle = fixed_goal()
    while abs(current_yaw - target_angle) < noise_tolerance:
        target_angle = fixed_goal()
    return target_angle

def relative_goal(object_current_pose):
    mode = 2
    
    if mode == 1:
        diff = 90 #degrees to the right
    elif mode == 2:
        diff = 180 #degrees to the right
    elif mode == 3:
        diff = 270 #degrees to the right
    elif mode == 4:
        return np.random.randint(30, 330) # anywhere to anywhere
    
    current_yaw = object_current_pose
    return (current_yaw + diff)%360

def relative_goal_90_180_270(object_current_pose):
    mode = np.random.randint(1, 4)
    logging.info(f"Target Angle Mode: {mode}")

    if mode == 1:
        diff = 90 #degrees to the right
    elif mode == 2:
        diff = 180 #degrees to the right
    elif mode == 3:
        diff = 270 #degrees to the right

    current_yaw = object_current_pose
    return (current_yaw + diff)%360 

class RotationEnvironment(Environment):
    def __init__(self, env_config : EnvironmentConfig, gripper_config : GripperConfig, object_config: ObjectConfig):
        super().__init__(env_config, gripper_config, object_config)

    # overriding method
    def choose_goal(self):
        object_state = self.actual_object_state() 
        if self.goal_selection_method == GOAL_SELECTION_METHOD.FIXED.value:
            return fixed_goals(object_state, self.noise_tolerance)
        elif self.goal_selection_method == GOAL_SELECTION_METHOD.RELATIVE.value:
            return relative_goal(object_state)
        elif self.goal_selection_method == GOAL_SELECTION_METHOD.RELATIVE_90_180_270.value:
            return relative_goal_90_180_270(object_state)
        
        raise ValueError(f"Goal selection method unknown: {self.goal_selection_method}")
    
    # overriding method 
    def reward_function(self, target_goal, yaw_before, yaw_after_rounded):

        if yaw_before is None: 
            logging.debug("Start Marker Pose is None")
            return 0, True

        if yaw_after_rounded is None:
            logging.debug("Final Marker Pose is None")
            return 0, True
        
        done = False

        yaw_before_rounded = round(yaw_before)
        yaw_after_rounded = round(yaw_after_rounded)

        goal_difference = self.rotation_min_difference(target_goal, yaw_after_rounded)
        delta_changes   = self.rotation_min_difference(target_goal, yaw_before_rounded) - self.rotation_min_difference(target_goal, yaw_after_rounded)
        
        logging.info(f"Yaw = {yaw_after_rounded}")

        if -self.noise_tolerance <= delta_changes <= self.noise_tolerance:
            reward = -1
        else:
            raw_reward = delta_changes/self.rotation_min_difference(target_goal, yaw_before_rounded)
            if (raw_reward >= REWARD_CONSTANTS.MAX_REWARD.value) :
                reward = 10
            elif (raw_reward <= REWARD_CONSTANTS.MIN_REWARD.value) :
                reward = -50
            else:
                reward = raw_reward

        precision_tolerance = 10
        if goal_difference <= precision_tolerance:
            logging.info("----------Reached the Goal!----------")
            reward += 10
            done = True

        return reward, done
