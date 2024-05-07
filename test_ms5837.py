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
logger.info("Testing ms5837")
serie.command.init_ms5837()
time.sleep(5)


def pressure_simple_callback(pressure):
    logger.info("Pressure callback called, and pressure is {pressure}".format(pressure=pressure))


serie.command.get_pressure()
time.sleep(1)
logger.info("Test completed")
serie.connection.close_conn()
