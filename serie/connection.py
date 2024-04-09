import threading
import time
from typing import Union

import serial
import serial.tools.list_ports
from serial import Serial
import logging
from serie import data

conn = None
logger = logging.getLogger(__name__)
read_t = None
motion_t = None
motion_update_gap = 0.01


# 连接
def connect(baud_rate=115200, update_motion_gap_=0.01, timeout=1):
    global conn
    global read_t
    global motion_t
    global motion_update_gap
    motion_update_gap = update_motion_gap_
    ports_list = list(serial.tools.list_ports.comports())
    if len(ports_list) == 0:
        logger.error("No serial ports, connection is not established")
    else:
        conn_ = serial.Serial(ports_list[0].device, baud_rate, timeout=timeout)
        if conn_.is_open:
            logger.info("Connected to stm32")
            conn = conn_
            # 启动读取进程
            read_t = threading.Thread(target=read_thread)
            read_t.start()
            # 启动更新动态进程
            motion_t = threading.Thread(target=data.motion_thread)
            motion_t.start()
        else:
            logger.error("Error connecting to stm32")


def read_thread():
    full_msg = ""
    logger.info("read stm32 message thread started")
    while is_connected():
        try:
            msg = get_conn().read(2)
            if msg:
                full_msg += str(msg)
                if full_msg.endswith("\r\n"):
                    full_msg = full_msg[:-2]
                    logger.debug("received message: {}".format(full_msg))
                    if full_msg.startswith("data"):
                        data.analyse(full_msg)
                    elif full_msg.startswith("rec_msg"):
                        logger.info("received message: {}".format(full_msg))
                    full_msg = ""
        except Exception as _:
            break
    logger.info("serie read thread dead")


# 关闭连接
def close_conn():
    global conn
    conn.close()
    if conn.is_open:
        logger.error("Error closing connection")
    else:
        conn = None
        logger.info("Successfully closed connection")


# 检查是否已经连接上
def is_connected():
    return conn is not None and conn.is_open


# 获取连接，使用前最好先检查是否有连接
def get_conn():
    if not is_connected():
        logger.error("Failed to get connection because no connection is established")
        raise Exception("No connection")
    else:
        return conn


def write(msg):
    get_conn().write(msg.encode('ascii'))
    logger.debug("sent msg: {}".format(msg))
