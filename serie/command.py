import logging

import serie.data
from serie import connection

logger = logging.getLogger(__name__)


def led(is_on):
    connection.write("led on" if is_on else "led off")


def set_pwm(index, speed):
    connection.write(f"pwm set {index} {speed}")


def update_pwm():
    connection.write("pwm get")


def get_pressure(callback=None):
    connection.write("pressure")
    serie.data.pressure_callback = callback


def send_lora_msg(msg):
    connection.write(f"lora {msg}")
