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
serie.command.send_lora_msg("hello lora")
time.sleep(10)
logger.info("Test completed")
serie.connection.close_conn()
