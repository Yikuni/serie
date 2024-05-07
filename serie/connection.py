import logging
import queue
import threading
import time

import serial
import serial.tools.list_ports
from serial import Serial
import logging
from serie import data

conn = None
logger = logging.getLogger(__name__)
read_t = None
motion_t = None
motion_update_gap = 0.1
write_lock = threading.RLock()
write_msg_queue = queue.Queue()


def get_ports():
    msg = ""
    names = [device.name for device in serial.tools.list_ports.comports()]
    for name in names:
        msg += name
        msg += "\n"
    msg = msg[:-1]
    return msg


# 连接
def connect(device_name=None, baud_rate=115200, port_index=0, update_motion_gap_=0.1, timeout=1):
    global conn
    global read_t
    global motion_t
    global motion_update_gap
    motion_update_gap = update_motion_gap_
    ports_list = list(serial.tools.list_ports.comports())
    if len(ports_list) == 0 and device_name is None:
        logger.error("No serial ports, connection failed to establish")
    else:
        if device_name is not None:
            conn_ = serial.Serial(device_name, baud_rate, timeout=timeout)
            logger.info(f"Connected to port {device_name}")

        else:
            conn_ = serial.Serial(ports_list[port_index].device, baud_rate, timeout=timeout)
            logger.info("Connected to port {}".format(ports_list[port_index].device))
        if conn_.is_open:
            conn = conn_
            # 启动读取进程
            read_t = threading.Thread(target=read_thread)
            read_t.start()
            # 启动写消息进程
            write_t = threading.Thread(target=write_thread)
            write_t.start()
        else:
            logger.info("Connection failed")

def read_thread():
    logger.info("read stm32 message thread started")
    while is_connected():
        try:
            msg = str(conn.read_until("\r\n".encode("ascii"), size=100), encoding="ascii")
            msg = msg[:-2]
            if msg:
                logger.debug("received message: {}".format(msg))
                if msg.startswith("data"):
                    data.analyse(msg)
                elif msg.startswith("ret_msg"):
                    logger.info("received message: {}".format(msg))
                    data.analyse_ret_msg(msg)
                else:
                    logger.info("received unknown message: {}".format(msg))
        except Exception as e:
            logger.error(e)
            break
    logger.info("serie read thread dead")


# 关闭连接
def close_conn():
    global conn
    write_lock.acquire()
    conn.close()
    if conn.is_open:
        logger.error("Error closing connection")
    else:
        conn = None
        logger.info("Successfully closed connection")
    write_lock.release()


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
    write_msg_queue.put(msg)
    logger.debug("sent msg: {}".format(msg))


def write_thread():
    while is_connected():
        time.sleep(0.01)
        if not write_msg_queue.empty():
            msg = write_msg_queue.get()
            get_conn().write((msg + ";").encode("ascii"))
            logger.debug("sent msg: {}".format(msg))
