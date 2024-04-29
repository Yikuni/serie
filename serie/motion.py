import time

import numpy as np
import logging

logger = logging.getLogger(__name__)


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
                    if abs(self.raw_motion_history[-j-1][i]) < self.filter_value:
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
