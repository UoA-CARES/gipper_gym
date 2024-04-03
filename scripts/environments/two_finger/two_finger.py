from abc import abstractmethod

import cv2
import tools.utils as utils
from configurations import GripperEnvironmentConfig
from environments.environment import Environment

from cares_lib.dynamixel.gripper_configuration import GripperConfig


class TwoFingerTask(Environment):
    def __init__(
        self,
        env_config: GripperEnvironmentConfig,
        gripper_config: GripperConfig,
    ):
        super().__init__(env_config, gripper_config)

    @abstractmethod
    def _reset(self):
        pass

    def _get_poses(self):
        """
        Gets the current state of the environment using the Aruco markers.

        Returns:
        dict : A dictionary containing the poses of the gripper and object markers.

        gripper: X-Y-Z-RPY Servos + X-Y-Z-RPY Finger-tips
        object: X-Y-Z-RPY Object
        """
        poses = {}

        # Servos + Finger Tips (2)
        num_gripper_markers = self.gripper.num_motors + 2

        # Gripper markers + Object (1)
        num_markers = num_gripper_markers + 1

        # maker_ids match servo ids (counting from 1)
        marker_ids = [id for id in range(1, num_markers + 1)]

        marker_poses = self._get_marker_poses(marker_ids, blindable=False)
        
        poses["gripper"] = dict(
            [i, marker_poses[i]] for i in range(1, num_gripper_markers + 1)
        )

        object_marker_id = num_markers
        poses["object"] = marker_poses[object_marker_id]

        return poses

    @abstractmethod
    def _environment_info_to_state(self, environment_info):
        pass

    def _get_environment_info(self):
        """
        Gets the current state of the environment based on the configured observation type (4 different options).

        Returns:
        A list representing the state of the environment.
        """
        environment_info = {}
        environment_info["gripper"] = self.gripper.state()
        environment_info["poses"] = self._get_poses()
        environment_info["goal"] = self.goal

        return environment_info

    @abstractmethod
    def _choose_goal(self):
        pass

    @abstractmethod
    def _reward_function(self, previous_state, current_state, goal_state):
        pass

    def _pose_to_state(self, pose):
        state = []
        position = pose["position"]
        state.append(position[0] - self.reference_position[0])  # X
        state.append(position[1] - self.reference_position[1])  # Y
        return state

    def _render_environment(self, state, environment_state):

        image = self.camera.get_frame()

        image = cv2.undistort(
            image, self.camera.camera_matrix, self.camera.camera_distortion
        )

        num_gripper_markers = self.gripper.num_motors + 2

        # account for servo positions and velocity values in state
        # base_index = self.gripper.num_motors + (
        #     self.gripper.num_motors if self.action_type == "velocity" else 0
        # )

        # account for velocity values in state
        base_index = (
            self.gripper.num_motors if self.action_type == "velocity" else 0
        )

        for i in range(0, num_gripper_markers):
            x = state[base_index + i * 2]
            y = state[base_index + i * 2 + 1]

            position = [
                x,
                y,
                environment_state["poses"]["gripper"][i + 1]["position"][2],
            ]

            reference = self.reference_position
            reference[2] = position[2]
            marker_pixel = utils.position_to_pixel(
                position,
                reference,
                self.camera.camera_matrix,
            )
            cv2.circle(image, marker_pixel, 9, (0, 255, 0), -1)

            cv2.putText(
                image,
                f"{i+1}",
                marker_pixel,
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                2,
                cv2.LINE_AA,
            )

        return image
