import time
import numpy as np
from serie import connection
import logging

logger = logging.getLogger(__name__)
raw_motion = np.zeros(6, dtype=np.float16)  # 加速度和角速度
motion = np.zeros(6, dtype=np.float16)  # 速度和角度
motion_last_update = 0
pwm_info = np.ones(4, dtype=np.int16) * 50


def analyse(msg):
    global raw_motion, motion, motion_last_update, pwm_info
    split_msg = msg.split()
    if split_msg[1] == "motion":
        # 更新速度
        raw_motion = np.array([float(word) for word in split_msg[2:]], dtype=np.float16)
        now = time.time()
        if motion_last_update != 0:
            motion += (now - motion_last_update) * raw_motion
        motion_last_update = now
    elif split_msg[1] == "pwm":
        # 更新pwm数值
        pwm_info = np.array([int(pwm_i) for pwm_i in split_msg[2:]], dtype=np.int16)


def motion_thread():
    logger.info("Motion thread started")
    while connection.is_connected():
        connection.write("motion")
        time.sleep(connection.motion_update_gap)
