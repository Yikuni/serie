import time

import numpy as np


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
            self.raw_motion_history.append(raw_motion.copy())
            self.velocity = self.updateVelocity(raw_motion[:3], delta_time)
            self.angle = self.updateAngle(raw_motion[3:], delta_time)
            self.motion_history.append(np.array([*self.velocity.copy(), *self.angle.copy()]))

    def updateVelocity(self, acc: np.ndarray, delta_time: float) -> np.ndarray:
        pass

    def updateAngle(self, av: np.ndarray, delta_time: float) -> np.ndarray:
        pass

    def correct_raw_motion(self):
        pass


class FirstMotionCalculator(MotionCalculator):
    def __init__(self):
        super().__init__()
        self.raw_motion_offset = np.zeros(6, dtype=np.float32)
    def updateVelocity(self, acc: np.ndarray, delta_time: float) -> np.ndarray:
        return self.velocity + acc * delta_time

    def updateAngle(self, av: np.ndarray, delta_time: float) -> np.ndarray:
        return self.angle + av * delta_time


    def correct_raw_motion(self):
        self.raw_motion_offset = np.array(self.raw_motion_history).mean(axis=0) - np.array([0, 0, 1, 0, 0, 0])
        self.motion_history = []
        self.raw_motion_history = []
        self.last_update_time = 0
        self.velocity = np.zeros(3, dtype=np.float32)
        self.angle = np.zeros(3, dtype=np.float32)
        self.acc = np.zeros(3, dtype=np.float32)
        self.av = np.zeros(3, dtype=np.float32)