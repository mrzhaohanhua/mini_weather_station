import os
import logging
import serial
import serial.tools.list_ports
from main import set_logging


def get_port_list() -> list:
    # 返回当前系统串口列表
    port_list = list(serial.tools.list_ports.comports())
    if len(port_list) == 0:
        logging.info("no serial port found.")
    else:
        logging.info(f"found serial ports: [{port_list}]")
    return port_list


def get_system_temperature() -> float:
    # 获取系统温度
    return int(os.popen("cat /sys/class/thermal/thermal_zone0/temp").read())/1000


if __name__ == "__main__":
    set_logging()
    logging.debug(f"get_system_temperature() = {get_system_temperature()}")
