import time
import numpy as np
from matplotlib import pyplot as plt, image
import threading
from serie import connection
import logging
from serie.motion import DMPMotionCalculator, MotionCalculator
from serie import command
logger = logging.getLogger(__name__)
pwm_info = np.ones(4, dtype=np.int16) * 50
pressure = 0.0
pressure_callback = None
motion_t = None
motion_calculator: MotionCalculator = DMPMotionCalculator()
ret_msg_analyzer = []
def analyse(msg):
    global pwm_info, pressure, pressure_callback
    split_msg = msg.split()
    if split_msg[1] == "motion":
        # 更新速度
        motion_calculator.update(
            np.array([float(word) for word in split_msg[2:]], dtype=np.float32)
        )
    elif split_msg[1] == "dmp":
        motion_calculator.update_dmp(
            np.array([float(word) for word in split_msg[2:]], dtype=np.float32)
        )
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

# msg格式： ret_msg 消息
def analyse_ret_msg(msg):
    for analyzer in ret_msg_analyzer:
        analyzer(msg)

#
def add_ret_msg_analyzer(analyzer_func):
    ret_msg_analyzer.append(analyzer_func)

def motion_thread():
    logger.info("Motion thread started")
    while connection.is_connected():
        connection.write("dmp")
        time.sleep(connection.motion_update_gap)
    logger.info("Motion thread dead")


def start_motion_thread():
    global motion_t
    # 启动更新动态进程
    motion_t = threading.Thread(target=motion_thread)
    motion_t.start()



def motion_history_plot():
    # 三轴速度
    motion_history = motion_calculator.motion_history.copy()
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
    motion_history = motion_calculator.motion_history.copy()
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
    raw_motion_history = motion_calculator.raw_motion_history.copy()
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
    raw_motion_history = motion_calculator.raw_motion_history.copy()
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

