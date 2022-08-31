import os
import time
import logging
import serial
import serial.tools.list_ports
from main import set_logging

BAUD_RATE = 9600
BYTE_SIZE = 8
PARITY = serial.PARITY_NONE
STOP_BIT = serial.STOPBITS_ONE
TIMEOUT = 5
WRITE_TIMEOUT = 5


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


def byteslist_to_stringlist(bl: bytes) -> list:
    number_list = list(bl)
    string_list = []
    for n in number_list:
        str = '0x{:02X}'.format(n)
        string_list.append(str)
    return string_list


def serial_demo():
    bytes_list = [0x05, 0x04, 0x10, 0x00, 0x00, 0x01, 0x34, 0xbd]
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=BAUD_RATE,
        bytesize=BYTE_SIZE,
        parity=PARITY,
        stopbits=STOP_BIT,
        timeout=TIMEOUT,
        write_timeout=WRITE_TIMEOUT)
    ser.flushInput()
    ser.flushOutput()
    ser.write(bytes_list)
    logging.debug(f"write data to '{ser.port}': {bytes_list}")
    time.sleep(1)
    recived_data = ser.read(7)
    if len(recived_data)==7:
        logging.debug(f"recived_data: {byteslist_to_stringlist(recived_data)}")
    else:
        logging.error(f"recived_data: {byteslist_to_stringlist(recived_data)}")
    pass


if __name__ == "__main__":
    set_logging()
    serial_demo()
