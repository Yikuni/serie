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
logger.info("Testing led flash twice")
for _ in range(2):
    serie.command.led(True)
    time.sleep(1)
    serie.command.led(False)
    time.sleep(1)
time.sleep(2)
logger.info("Testing led flash 3 times")
for _ in range(3):
    serie.command.led(True)
    time.sleep(1)
    serie.command.led(False)
    time.sleep(1)
logger.info("Testing thrusters in order")
for i in range(6):
    serie.command.set_pwm(i, 120)
    time.sleep(1)
    serie.command.set_pwm(i, 180)
    time.sleep(1)
    serie.command.set_pwm(i, 220)
    time.sleep(1)
    serie.command.set_pwm(i, 280)
    time.sleep(1)
    serie.command.set_pwm(i, 50)
    time.sleep(1)
logger.info("Testing ms5837")
serie.command.init_ms5837()
time.sleep(5)


def pressure_simple_callback(pressure):
    logger.info("Pressure callback called, and pressure is {pressure}".format(pressure=pressure))


serie.command.get_pressure()
time.sleep(1)
logger.info("Test completed")
serie.connection.close_conn()
