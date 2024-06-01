import time

import numpy as np
import logging
from enum import Enum

logger = logging.getLogger(__name__)
from serie import command


def rotate_vector(x, y, z, theta_x, theta_y, theta_z):
    vector = np.array([x, y, z])

    # 三轴旋转角度
    theta_x = np.radians(theta_x)  # 将角度转换为弧度
    theta_y = np.radians(theta_y)
    theta_z = np.radians(theta_z)

    # 绕 x 轴的旋转矩阵
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(theta_x), -np.sin(theta_x)],
        [0, np.sin(theta_x), np.cos(theta_x)]
    ])

    # 绕 y 轴的旋转矩阵
    Ry = np.array([
        [np.cos(theta_y), 0, np.sin(theta_y)],
        [0, 1, 0],
        [-np.sin(theta_y), 0, np.cos(theta_y)]
    ])

    # 绕 z 轴的旋转矩阵
    Rz = np.array([
        [np.cos(theta_z), -np.sin(theta_z), 0],
        [np.sin(theta_z), np.cos(theta_z), 0],
        [0, 0, 1]
    ])

    # 将三个旋转矩阵相乘得到总的旋转矩阵
    R_total = np.matmul(Rz, np.matmul(Ry, Rx))

    # 将原始向量应用旋转矩阵得到旋转后的向量
    return np.matmul(R_total, vector)


class MotionCalculator:

    def __init__(self):
        self.velocity = np.zeros(3, dtype=np.float32)
        self.angle = np.zeros(3, dtype=np.float32)
        self.acc = np.zeros(3, dtype=np.float32)
        self.av = np.zeros(3, dtype=np.float32)
        self.motion_history = []
        self.raw_motion_history = []
        self.last_update_time = 0

    def update(self, raw_motion: np.ndarray):
        if self.last_update_time == 0:
            self.last_update_time = time.time()
        else:
            now = time.time()
            delta_time = now - self.last_update_time
            self.last_update_time = now
            raw_motion = self.correct_acc(raw_motion)
            self.raw_motion_history.append(raw_motion.copy())
            self.velocity = self.update_velocity(raw_motion[:3], delta_time)
            self.angle = self.update_angle(raw_motion[3:], delta_time)
            self.motion_history.append(np.array([*self.velocity.copy(), *self.angle.copy()]))

    def update_dmp(self, dmp_data: np.ndarray):
        self.angle = np.array([-dmp_data[1], -dmp_data[0], dmp_data[2]])

    def update_velocity(self, acc: np.ndarray, delta_time: float) -> np.ndarray:
        raise NotImplementedError()

    def update_angle(self, av: np.ndarray, delta_time: float) -> np.ndarray:
        raise NotImplementedError()

    def correct_acc(self, raw_motion: np.ndarray) -> np.ndarray:
        raise NotImplementedError()

    def correct_raw_motion(self):
        raise NotImplementedError()

    def clear_other_data(self):
        return

    def clear_data(self):
        self.velocity = np.zeros(3, dtype=np.float32)
        self.angle = np.zeros(3, dtype=np.float32)
        self.acc = np.zeros(3, dtype=np.float32)
        self.av = np.zeros(3, dtype=np.float32)
        self.motion_history = []
        self.raw_motion_history = []
        self.last_update_time = 0
        self.clear_other_data()


class DMPMotionCalculator(MotionCalculator):
    def __init__(self):
        super().__init__()
        self.raw_motion_offset = np.zeros(6, dtype=np.float32)
        self.filter_size = 3
        self.filter_value = 0.005

    def update_velocity(self, acc: np.ndarray, delta_time: float) -> np.ndarray:
        if len(self.raw_motion_history) > self.filter_size:
            for i in range(self.filter_size):
                for j in range(self.filter_size):
                    if abs(self.raw_motion_history[-j - 1][i]) < self.filter_value:
                        return self.velocity
                acc[i] = np.array(self.raw_motion_history)[-self.filter_size:, i].mean()
            return self.velocity + acc * delta_time
        else:
            return self.velocity

    def update_angle(self, av: np.ndarray, delta_time: float) -> np.ndarray:
        return self.angle

    def correct_acc(self, raw_motion: np.ndarray) -> np.ndarray:
        raw_motion[:3] += - self.raw_motion_offset[:3] - rotate_vector(0, 0, 1, *self.angle)
        return raw_motion

    def correct_raw_motion(self):
        self.raw_motion_offset = np.array(self.raw_motion_history).mean(axis=0)
        self.motion_history.clear()
        self.raw_motion_history.clear()
        self.last_update_time = 0
        self.velocity = np.zeros(3, dtype=np.float32)
        self.angle = np.zeros(3, dtype=np.float32)
        self.acc = np.zeros(3, dtype=np.float32)
        self.av = np.zeros(3, dtype=np.float32)
        logger.info("corrected raw motion")

    def clear_other_data(self):
        self.raw_motion_offset = np.zeros(6, dtype=np.float32)


class MotionState(Enum):
    TILT_LEFT = [(0, 195), (1, 199), (4, 193), (5, 199)]  # 向左倾斜
    TILT_RIGHT = [(0, 199), (1, 193), (4, 199), (5, 195)]  # 向右倾斜
    NO_TILT = [(0, 201), (1, 195), (4, 195), (5, 201)]  # 不倾斜 ok
    TURN_LEFT = [(2, 193), (3, 180)]  # 左转
    TURN_RIGHT = [(2, 180), (3, 192)]  # 右转
    NO_TURN = [(2, 177), (3, 178)]  # 直行
    STOP = [(2, 50), (3, 50)]  # 停止
    UP = [(0, -1), (1, -1), (4, -1), (5, -1)]
    DOWN = [(0, 1), (1, 1), (4, 1), (5, 1)]
    NO_UP_OR_DOWN = [(0, 0)]
    def __init__(self, pwm_list):
        self.pwm_list = pwm_list

    def activate(self, offset=None):
        for p in self.pwm_list:
            if offset is not None and offset.__contains__(p[0]):
                command.set_pwm(p[0], p[1] + offset[p[0]])
            else:
                command.set_pwm(p[0], p[1])



class MotionController:
    def __init__(self):
        self.state1 = MotionState.STOP
        self.state2 = MotionState.NO_TILT
        self.state3 = MotionState.NO_UP_OR_DOWN

    @staticmethod
    def init_pwm():
        for i in range(6):
            command.set_pwm(i, 50)
            time.sleep(0.5)
            command.set_pwm(i, 150)
            time.sleep(0.5)
            command.set_pwm(i, 50)
            time.sleep(0.5)

    def update_state(self, state: MotionState):
        if state in (MotionState.STOP, MotionState.NO_TURN, MotionState.TURN_LEFT, MotionState.TURN_RIGHT):
            if self.state1 != state:
                self.state1 = state
                state.activate()
        elif state in (MotionState.NO_UP_OR_DOWN, MotionState.UP, MotionState.DOWN):
            self.state3 = state
            self.state2.activate({key: value for key, value in self.state3.pwm_list})
        else:
            if self.state2 != state:
                self.state2 = state
                state.activate({key: value for key, value in self.state3.pwm_list})
