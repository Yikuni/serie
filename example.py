import time

import serie
import logging

logging.basicConfig(level=logging.INFO, filename='log.log', filemode='w',
                    format="%(asctime)s - %(name)s - %(levelname)-9s: %(message)s"
                    , datefmt="%Y-%m-%d %H:%M:%S")
serie.connection.connect()
if serie.connection.is_connected():
    # serie.command.led(True)
    time.sleep(2)
    # serie.command.led(False)
    serie.command.update_pwm()
    pwm_info = serie.data.pwm_info
    serie.command.set_pwm(0, 100)
    time.sleep(2)
    serie.command.set_pwm(0, 50)
serie.connection.close_conn()
