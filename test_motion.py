import time
import logging

import serie

logging.basicConfig(level=logging.INFO, filename='log.log', filemode='w+',
                    format="%(asctime)s - %(name)-20s - %(levelname)-9s: %(message)s"
                    , datefmt="%Y-%m-%d %H:%M:%S")
console = logging.StreamHandler()
logging.getLogger().addHandler(console)
logger = logging.getLogger(__name__)
serie.connection.connect(device_name="/dev/ttyS5")
time.sleep(1)
serie.command.init_dmp()	# 初始化dmp
time.sleep(5)
serie.data.start_motion_thread()	# 开启读取stm32姿态数据的进程
for i in range(5):
    if len(serie.data.motion_calculator.raw_motion_history) == 0:
        i -= 1
        continue
    logger.info(serie.data.motion_calculator.raw_motion_history[-1])
    time.sleep(1)
serie.command.stop_dmp()	# 开启stm32内部持续读取dmp
serie.connection.close_conn()