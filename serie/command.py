import logging
from serie import connection

logger = logging.getLogger(__name__)


def led(is_on):
    connection.write("led on" if is_on else "led off")


def set_pwm(index, speed):
    connection.write(f"pwm set {index} {speed}")


def update_pwm():
    connection.write("pwm get")
