import threading
from typing import Union

import serial
import serial.tools.list_ports
from serial import Serial
import logging
from serie import data

conn = None
logger = logging.getLogger(__name__)
debug_thread = None


# 连接
def connect(baud_rate=115200, timeout=1):
    global conn
    global debug_thread
    ports_list = list(serial.tools.list_ports.comports())
    if len(ports_list) == 0:
        logger.error("No serial ports, connection is not established")
    else:
        conn_ = serial.Serial(ports_list[0].device, baud_rate, timeout=timeout)
        if conn_.is_open:
            logger.info("Connected to stm32")
            conn = conn_
            debug_thread = threading.Thread(target=read_thread)
            debug_thread.start()
        else:
            logger.error("Error connecting to stm32")


def read_thread():
    full_msg = ""
    while True:
        if is_connected():
            try:
                msg = get_conn().read(2)
                if msg:
                    full_msg += str(msg)
                    if full_msg.endswith("\r\n"):
                        full_msg = full_msg[:-2]
                        logger.debug("received message: {}".format(full_msg))
                        if full_msg.startswith("data"):
                            data.analyse(full_msg)
                        full_msg = ""
            except Exception as _:
                break
        else:
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
