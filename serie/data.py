import time
import numpy as np

raw_motion = np.zeros(6, dtype=np.float16)  # 加速度和角速度
motion = np.zeros(6, dtype=np.float16)  # 速度和角度
last_update = 0


def analyse(msg):
    global raw_motion, motion, last_update
    split_msg = msg.split()
    if split_msg[1] == "motion":
        raw_motion = np.array([float(word) for word in split_msg[2:]], dtype=np.float16)
        now = time.time()
        if last_update != 0:
            motion += (now - last_update) * raw_motion
        last_update = now
