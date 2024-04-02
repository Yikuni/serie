import time

import serie
import logging

logging.basicConfig(level=logging.DEBUG, filename='log.log', filemode='w',
                    format="%(asctime)s - %(name)s - %(levelname)-9s: %(message)s"
                    , datefmt="%Y-%m-%d %H:%M:%S")
serie.connection.connect()
if serie.connection.is_connected():
    serie.command.led(True)
    time.sleep(2)
    serie.command.led(False)
serie.connection.close_conn()
