import time
import numpy as np
from matplotlib import pyplot as plt, image
import threading
from serie import connection
import logging

logger = logging.getLogger(__name__)
raw_motion = np.zeros(6, dtype=np.float32)  # 加速度和角速度
raw_motion_offset = np.zeros(6, dtype=np.float32)
motion = np.zeros(6, dtype=np.float32)  # 速度和角度
motion_last_update = 0
pwm_info = np.ones(4, dtype=np.int16) * 50
motion_history = []
raw_motion_history = []
pressure = 0.0
pressure_callback = None
motion_t = None


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


def cal_raw_motion_offset():
    global raw_motion_offset, motion_history, raw_motion_history, motion, raw_motion, motion_last_update
    raw_motion_offset = np.array(raw_motion_history).mean(axis=0) - np.array([0, 0, 1, 0, 0, 0])
    motion_history = []
    raw_motion_history = []
    motion_last_update = 0
    raw_motion = np.zeros(6, dtype=np.float32)  # 加速度和角速度
    motion = np.zeros(6, dtype=np.float32)  # 速度和角度
def analyse(msg):
    global raw_motion, motion, motion_last_update, pwm_info, pressure, pressure_callback
    split_msg = msg.split()
    if split_msg[1] == "motion":
        # 更新速度
        _raw_motion = np.array([float(word) for word in split_msg[2:]], dtype=np.float32) - raw_motion_offset

        raw_motion = _raw_motion.copy()
        raw_motion_history.append(raw_motion.copy())
        now = time.time()
        _motion = motion.copy()
        if motion_last_update != 0:
            delta_t = now - motion_last_update  # 单位是s
            motion_last_update = now
            _raw_motion[:3] = rotate_vector(*_raw_motion[:3], *(_motion[3:]))
            _raw_motion[3:] = rotate_vector(*_raw_motion[3:], *(_motion[3:]))
            _raw_motion = _raw_motion - np.array([0, 0, 1, 0, 0, 0])

            # 降噪
            _raw_motion[:3] = np.where(_raw_motion < 0.05, 0, _raw_motion)[:3]
            _raw_motion[3:] = np.where(_raw_motion < 2, 0, _raw_motion)[3:]

            _motion[:3] = _motion[:3] + _raw_motion[:3] * delta_t
            _motion[3:] = _motion[3:] + _raw_motion[3:] * delta_t
            motion = _motion
        else:
            motion_last_update = now
        # 将速度加入历史
        motion_history.append(motion.copy())
    elif split_msg[1] == "pwm":
        # 更新pwm数值
        pwm_info = np.array([int(pwm_i) for pwm_i in split_msg[2:]], dtype=np.int16)
    elif split_msg[1] == "pressure":
        # 获取压强
        logger.info(f"received pressure {split_msg[2]}")
        pressure = float(split_msg[2])
        if pressure_callback is not None:
            pressure_callback(pressure)
            pressure_callback = None


def motion_thread():
    logger.info("Motion thread started")
    while connection.is_connected():
        connection.write("motion")
        time.sleep(connection.motion_update_gap)
    logger.info("Motion thread dead")


def start_motion_thread():
    global motion_t
    # 启动更新动态进程
    motion_t = threading.Thread(target=motion_thread)
    motion_t.start()



def motion_history_plot():
    # 三轴速度
    if len(motion_history) == 0:
        return "motion.png"
    motion_his = np.array(motion_history)
    plt.figure(1)
    plt.clf()
    for i in range(3):
        plt.subplot(3, 1, i + 1)
        plt.plot(range(len(motion_his)), motion_his[:, i])
    plt.savefig("motion.png")
    return "motion.png"
def motion_history_plot2():
    # 三轴速度
    if len(motion_history) == 0:
        return "motion2.png"
    motion_his = np.array(motion_history)
    plt.figure(2)
    plt.clf()
    for i in range(3):
        plt.subplot(3, 1, i + 1)
        plt.plot(range(len(motion_his)), motion_his[:, i+3])
    plt.savefig("motion2.png")
    return "motion2.png"

def raw_motion_history_plot():
    # 三轴速度
    if len(raw_motion_history) == 0:
        return "raw_motion.png"
    raw_motion_his = np.array(raw_motion_history)
    plt.figure(3)
    plt.clf()
    for i in range(3):
        plt.subplot(3, 1, i + 1)
        plt.plot(range(len(raw_motion_his)), raw_motion_his[:, i])
    plt.savefig("raw_motion.png")
    return "raw_motion.png"


def raw_motion_history_plot2():
    # 三轴速度
    if len(raw_motion_history) == 0:
        return "raw_motion2.png"
    raw_motion_his = np.array(raw_motion_history)
    plt.figure(4)
    plt.clf()
    for i in range(3):
        plt.subplot(3, 1, i + 1)
        plt.plot(range(len(raw_motion_his)), raw_motion_his[:, i+3])
    plt.savefig("raw_motion2.png")
    return "raw_motion2.png"
def is_motion_t_alive():
    return motion_t is not None and motion_t.is_alive()

def init_motion_data():
    global raw_motion, raw_motion_offset, raw_motion_history, motion, motion_last_update, motion_history
    raw_motion = np.zeros(6, dtype=np.float16)  # 加速度和角速度
    raw_motion_offset = np.zeros(6, dtype=np.float16)
    motion = np.zeros(6, dtype=np.float16)  # 速度和角度
    motion_last_update = 0
    motion_history = []
    raw_motion_history = []