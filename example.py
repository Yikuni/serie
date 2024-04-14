import time

import serie
import logging

logging.basicConfig(level=logging.INFO, filename='log.log', filemode='w',
                    format="%(asctime)s - %(name)-20s - %(levelname)-9s: %(message)s"
                    , datefmt="%Y-%m-%d %H:%M:%S")
console = logging.StreamHandler()
logging.getLogger().addHandler(console)
serie.connection.connect(port_index=1)  # 用电脑调试的时候用
# serie.connection.connect(port_index=0)  # 实机使用
if serie.connection.is_connected():
    time.sleep(1)
    serie.command.led(False)
    time.sleep(1)
    serie.command.led(True)
    time.sleep(1)
    serie.command.update_pwm()
    time.sleep(1)
    pwm_info = serie.data.pwm_info
    serie.command.set_pwm(0, 100)
    time.sleep(2)
    serie.command.set_pwm(0, 50)
    time.sleep(1)
serie.connection.close_conn()
