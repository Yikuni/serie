import time
import numpy as np
from matplotlib import pyplot as plt, image

from serie import connection
import logging

logger = logging.getLogger(__name__)
raw_motion = np.zeros(6, dtype=np.float16)  # 加速度和角速度
motion = np.zeros(6, dtype=np.float16)  # 速度和角度
motion_last_update = 0
pwm_info = np.ones(4, dtype=np.int16) * 50
motion_history = []
pressure = 0.0
pressure_callback = None


def analyse(msg):
    global raw_motion, motion, motion_last_update, pwm_info, pressure, pressure_callback
    split_msg = msg.split()
    if split_msg[1] == "motion":
        # 更新速度
        raw_motion = np.array([float(word) for word in split_msg[2:]], dtype=np.float16)
        now = time.time()
        if motion_last_update != 0:
            motion += (now - motion_last_update) * raw_motion
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


def motion_history_plot():
    # 三轴速度
    if len(motion_history) == 0:
        return "motion.png"
    motion_his = np.array(motion_history)
    for i in range(3):
        plt.subplot(3, 1, i+1)

        plt.plot(range(len(motion_his)), motion_his[:, i])
    plt.savefig("motion.png")
    return "motion.png"