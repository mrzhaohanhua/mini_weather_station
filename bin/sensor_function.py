import os
import time
import logging
import serial
import serial.tools.list_ports
import crc
from main import set_logging

SERIAL_TIME_SPOT = 1
BAUD_RATE = 9600
BYTE_SIZE = 8
PARITY = serial.PARITY_NONE
STOP_BIT = serial.STOPBITS_ONE
TIMEOUT = 10
WRITE_TIMEOUT = 5

GET_CONTROLLER_DATA_COMMAND = 4
GET_CONTROLLER_CONFIG_COMMAND = 3
SET_CONTROLLER_CONFIG_COMMAND = 6

DEFAULT_DATA_BYTES = 2  # 默认内存地址对应的字节数


def get_port_list() -> list:
    # 返回当前系统串口列表
    port_list = list(serial.tools.list_ports.comports())
    if len(port_list) == 0:
        logging.info("no serial port found.")
    else:
        logging.info(f"found serial ports: [{port_list}]")
    return port_list


def command(port: str, dev_addr: int, command: int, addr: list, length: int, data_bytes=DEFAULT_DATA_BYTES) -> list:
    command_list = []
    ser = serial.Serial(
        port=port,
        baudrate=BAUD_RATE,
        bytesize=BYTE_SIZE,
        parity=PARITY,
        stopbits=STOP_BIT,
        timeout=TIMEOUT,
        write_timeout=WRITE_TIMEOUT)
    command_list.append(dev_addr)
    command_list.append(command)
    command_list = command_list+addr
    command_list = command_list+number_to_list(length, 2)
    command_list = crc.append_crc(command_list)
    ser.flushInput()
    ser.flushOutput()
    logging.debug(f"'{port}' write: {byteslist_to_stringlist(command_list)}")
    ser.write(command_list)
    time.sleep(SERIAL_TIME_SPOT)
    expect_receive_length = 1+1+1+length*data_bytes+2
    receive_data = list(ser.read(expect_receive_length))
    if len(receive_data) == expect_receive_length:
        if crc.crc_check(receive_data):
            logging.debug(
                f"'{port}' receive: {byteslist_to_stringlist(receive_data)}")
        else:
            logging.error(
                f"'{port}' receive: {byteslist_to_stringlist(receive_data)}, but CRC check failed.")
    else:
        logging.info(f"'{port}' receive nothing.")
    return receive_data


def get_system_temperature() -> float:
    # 获取系统温度
    return int(os.popen("cat /sys/class/thermal/thermal_zone0/temp").read())/1000


def number_to_list(number: int, len: int) -> list:
    if len == 1:
        if number < 256:
            return [number]
        else:
            return []
    elif len == 2:
        if number < 0x100:
            return [0, number]
        elif number < 0x10000:
            return [int(number / 0x100), number % 0x100]
    else:
        return []


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
    time.sleep(SERIAL_TIME_SPOT)
    recived_data = ser.read(7)
    if len(recived_data) == 7:
        logging.debug(f"recived_data: {byteslist_to_stringlist(recived_data)}")
    else:
        logging.error(f"recived_data: {byteslist_to_stringlist(recived_data)}")
    pass


if __name__ == "__main__":
    set_logging()
    command('/dev/ttyUSB0', 0x6, GET_CONTROLLER_DATA_COMMAND,
            [0x10, 0x00], 29)
    pass
