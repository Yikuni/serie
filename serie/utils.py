import time

import serie.command
from serie import data

def dmp_init_listener(msg):
    if msg.startswith('ret_msg dmp init success'):
        time.sleep(3)
        serie.command.start_dmp()


data.add_ret_msg_analyzer(dmp_init_listener)