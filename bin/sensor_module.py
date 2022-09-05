from audioop import add
from distutils.log import error
import sys
import os
import json
import time
import logging
import serial
import serial.tools.list_ports
import crc
import threading
import aliyun_iot


BAUD_RATE_LIST = [9600, 19200]
BAUD_RATE = 9600                # 串口速率
BYTE_SIZE = 8                   # 串口字节大小
PARITY = serial.PARITY_NONE     # 串口奇偶校验
STOP_BIT = serial.STOPBITS_ONE  # 串口停止位
READ_TIME_SPOT = 1              # 数据读取间隔
TIMEOUT = 10                    # 数据读取超时
WRITE_TIMEOUT = 5               # 数据写入超时

GET_CONTROLLER_DATA_COMMAND = 0x04          # 读取控制器运行数据的指令
GET_CONTROLLER_CUSTOM_DATA_COMMAND = 0x03   # 读取控制器设置的指令
SET_CONTROLLER_CUSTOM_DATA_COMMAND = 0x06   # 写入控制器设置的指令
GET_SENSOR_DATA_COMMAND = 0x03  # 读取传感器数据的指令
SET_SENSOR_CUSTOM_DATA_COMMAND = 0x06  # 设置传感器数据的指令

DEFAULT_DATA_UNIT = 16  # 寄存器大小 bit


def load_controller_config() -> bool:
    # 读取控制器配置文件
    global controller_config
    controller_config = {}
    controller_config_file_name = "./data/controller_config.json"
    try:
        logging.debug(
            f"load controller config file '{controller_config_file_name}'")
        with open(controller_config_file_name, 'r', encoding='UTF-8') as controller_config_file:
            controller_config = json.load(controller_config_file)
    except FileNotFoundError:
        logging.error(
            f"controller config file '{controller_config_file_name}' not found.")
        return False
    # 验证配置有效性
    for n in range(3):
        response = send_command(
            controller_config.get("serial_port", ""),
            controller_config.get("device_addr", -1),
            GET_CONTROLLER_DATA_COMMAND,
            [0x10, 0x00],
            1,
            DEFAULT_DATA_UNIT)
        if len(response) > 0:
            logging.debug(f"controller config file checked.")
            return True
        time.sleep(1)
    logging.error(
        f"controller config file '{controller_config_file_name}' is not valid.")
    return False


def load_sensor_config() -> bool:
    # 读取传感器配置文件
    global sensor_config
    sensor_config = {}
    sensor_config_file_name = "./data/sensor_config.json"
    try:
        logging.debug(
            f"load sensor config file '{sensor_config_file_name}'")
        with open(sensor_config_file_name, 'r', encoding='UTF-8') as sensor_config_file:
            sensor_config = json.load(sensor_config_file)
    except FileNotFoundError:
        logging.error(
            f"sensor config file '{sensor_config_file_name}' not found.")
        return False
    # 验证配置有效性
    for n in range(3):
        response = send_command(
            sensor_config.get("serial_port", ""),
            sensor_config.get("device_addr", -1),
            GET_SENSOR_DATA_COMMAND,
            [0x00, 0x00],
            1,
            DEFAULT_DATA_UNIT)
        if len(response) > 0:
            logging.debug(f"sensor config file checked.")
            return True
        time.sleep(1)
    logging.error(
        f"sensor config file '{sensor_config_file_name}' is not valid.")
    return False


def get_port_list() -> list:
    # 返回当前系统串口列表
    port_list = list(p.device for p in serial.tools.list_ports.comports())
    if len(port_list) == 0:
        logging.info("no serial port found.")
    else:
        logging.info(f"found serial ports: [{port_list}]")
    return port_list


def send_command(port: str, dev_addr: int, command_code: int, addr: list, length: int, data_unit=DEFAULT_DATA_UNIT, baud_rate=BAUD_RATE, time_out=TIMEOUT) -> list:
    # 发送指令，并接收返回的数据
    command_list = []
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baud_rate,
            bytesize=BYTE_SIZE,
            parity=PARITY,
            stopbits=STOP_BIT,
            timeout=time_out,
            write_timeout=WRITE_TIMEOUT)
        logging.debug(
            f"'{port}' open: baudrate:{baud_rate}, address:{byteslist_to_stringlist(addr)}")
    except:
        logging.error(f"'{port}' open fail")
        return []

    # 开始组合命令
    command_list.append(dev_addr)  # 设备地址
    command_list.append(command_code)  # 指令代码
    command_list = command_list+addr  # 寄存器地址
    command_list = command_list+number_to_byteslist(length, 2)  # 需要的数据长度
    command_list = crc.append_crc(command_list)  # 奇偶校验
    ser.flushInput()
    ser.flushOutput()
    logging.debug(f"'{port}' write: {byteslist_to_stringlist(command_list)}")
    ser.write(command_list)
    time.sleep(READ_TIME_SPOT)  # 等候时间到了再继续执行
    # 期望的数据长度(字节)
    expect_receive_length = 1+1+1+length * int(data_unit/ser.bytesize)+2
    receive_data = list(ser.read(expect_receive_length))
    if len(receive_data) == expect_receive_length:
        if crc.crc_check(receive_data):
            logging.debug(
                f"'{port}' receive: {byteslist_to_stringlist(receive_data)}")
        else:
            logging.error(
                f"'{port}' receive: {byteslist_to_stringlist(receive_data)}, but CRC check failed.")
    else:
        logging.debug(f"'{port}' receive nothing.")
    return receive_data


def get_system_temperature() -> float:
    # 获取系统温度
    return int(os.popen("cat /sys/class/thermal/thermal_zone0/temp").read())/1000


def number_to_byteslist(number: int, len: int) -> list:
    # 数字转为指定位数的字节列表
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


def byteslist_to_number(bytes_list: list) -> int:
    # 2或者4字节数据转为整数
    if len(bytes_list) == 2:
        return bytes_list[0]*0x100+bytes_list[1]
    elif len(bytes_list) == 4:
        return bytes_list[0]*0x1000000 + bytes_list[1]*0x10000 + bytes_list[2]*0x100 + bytes_list[3]


def byteslist_to_stringlist(bl: bytes) -> list:
    # 字节列表转为Hex字符串列表
    number_list = list(bl)
    string_list = []
    for n in number_list:
        str = '0x{:02X}'.format(n)
        string_list.append(str)
    return string_list


def get_controller_data() -> dict:
    port = controller_config.get("serial_port", "")
    dev_addr = controller_config.get("device_addr", -1)
    for n in range(3):
        recived_data = send_command(
            port, dev_addr, GET_CONTROLLER_DATA_COMMAND, [0x10, 0x00], 29)
        if len(recived_data) > 0:
            break
        time.sleep(1)
    if len(recived_data) == 0:
        return {}
    # 将bytes list 转为控制器数据字典
    if len(recived_data) != 63:
        logging.warning("传递的controller数据字节列表不合法.")
        return {}
    # 生成data_frame
    data_frame_dict = {}
    for offset in range(29):
        data_frame_dict['0x{:02X}'.format(
            0x1000+offset)] = byteslist_to_number(recived_data[3+offset*2:3+offset*2+2])
    # 将data_frame写入文件
    controller_data_file_name = "./data/controller_data.json"
    controller_data = {}
    try:
        with open(controller_data_file_name, 'w', encoding='UTF-8') as controller_data_file:
            controller_data["time"] = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime())
            controller_data.update(data_frame_dict)
            json.dump(controller_data, controller_data_file,
                      ensure_ascii=False, indent=2)
    except:
        logging.warning(
            f"controller data file '{controller_data_file_name}' write fail.")

    data_dict = {}
    data_dict["controller_soft_ver"] = data_frame_dict.get("0x1000", "")
    data_dict["controller_panel_volt"] = \
        float('%0.2f' % (data_frame_dict.get("0x1001", 0)*0.1))
    data_dict["controller_batt_volt"] = \
        float('%0.2f' % (data_frame_dict.get("0x1002", 0)*0.1))
    data_dict["controller_charge_curr"] = \
        float('%0.2f' % (data_frame_dict.get("0x1005", 0)*0.1))
    data_dict["controller_charge_temp"] =\
        float('%0.2f' % (data_frame_dict.get("0x1006", 0)))
    data_dict["controller_charge_power"] = \
        float('%0.2f' % (data_frame_dict.get("0x1007", 0)*0.1))
    data_dict["controller_load_power"] =\
        float('%0.2f' % (data_frame_dict.get("0x1008", 0)*0.1))
    data_dict["controller_batt"] = \
        float('%0.2f' % (data_frame_dict.get("0x1009", 0)))
    data_dict["controller_load_curr"] =\
        float('%0.2f' % (data_frame_dict.get("0x100C", 0)))

    # 处理控制器错误消息
    error_messages = get_controller_error_messages(
        data_frame_dict.get("0x1013", 0))
    if len(error_messages) > 0:
        logging.warning(f"controller report errors: {error_messages}")

    return data_dict


def get_controller_custom_data() -> dict:
    # 读取控制器客户设置参数
    port = controller_config.get("serial_port", "")
    dev_addr = controller_config.get("device_addr", -1)
    for n in range(3):  # 最多循环3次
        recived_data = send_command(
            port, dev_addr, GET_CONTROLLER_CUSTOM_DATA_COMMAND, [0x10, 0x24], 39)
        if len(recived_data) > 0:
            break
        time.sleep(1)
    if len(recived_data) == 0:
        return {}
    data_frame_dict = {}
    for offset in range(39):
        data_frame_dict['0x{:02X}'.format(
            0x1024+offset)] = byteslist_to_number(recived_data[3+offset*2:3+offset*2+2])
    data_dict = {}
    data_dict["超压电压"] =\
        float('%0.2f' % (data_frame_dict.get("0x1024", None)*0.1))
    data_dict["充电限制电压"] = \
        float('%0.2f' % (data_frame_dict.get("0x1025", None)*0.1))
    data_dict["超压恢复电压"] = \
        float('%0.2f' % (data_frame_dict.get("0x1026", None)*0.1))
    data_dict["均衡充电电压"] = \
        float('%0.2f' % (data_frame_dict.get("0x1027", None)*0.1))
    data_dict["提升充电电"] = \
        float('%0.2f' % (data_frame_dict.get("0x1028", None)*0.1))
    data_dict["提升充电返回电压"] = \
        float('%0.2f' % (data_frame_dict.get("0x1029", None)*0.1*0.1))
    data_dict["浮充充电电压"] = \
        float('%0.2f' % (data_frame_dict.get("0x102A", None)*0.1))
    data_dict["过放电压"] = \
        float('%0.2f' % (data_frame_dict.get("0x102B", None)*0.1))
    data_dict["过放恢复电压"] = \
        float('%0.2f' % (data_frame_dict.get("0x102C", None)*0.1))
    data_dict["电池欠压"] = data_frame_dict.get("0x102D", None)*0.1
    data_dict["均衡充电时间"] = data_frame_dict.get("0x102E", None)
    data_dict["提升充电时间"] = data_frame_dict.get("0x102F", None)
    data_dict["温度补偿系数"] = data_frame_dict.get("0x1030", None)
    data_dict["设备地址"] = data_frame_dict.get("0x1031", None)
    data_dict["光控开启电压"] = data_frame_dict.get("0x1032", None)
    data_dict["光控关闭电压"] = data_frame_dict.get("0x1033", None)
    data_dict["光控开时段1"] = data_frame_dict.get("0x1034", None)
    data_dict["光控开时段2"] = data_frame_dict.get("0x1035", None)
    data_dict["户用和路灯模式"] = data_frame_dict.get("0x1036", None)
    data_dict["定时关负载"] = data_frame_dict.get("0x1037", None)
    data_dict["充电开/关机"] = data_frame_dict.get("0x1038", None)
    data_dict["蜂鸣器使能"] = data_frame_dict.get("0x1039", None)
    data_dict["蓄电池串数"] = data_frame_dict.get("0x103A", None)
    data_dict["电池类型"] = data_frame_dict.get("0x103B", None)
    data_dict["负载开/关机"] = data_frame_dict.get("0x103C", None)

    return data_dict


def get_controller_error_messages(error_value: int) -> list:
    # 读取错误代码
    error_value = error_value & 0b1101111111111111  # 屏蔽第13位错误(蓄电池温度传感器失效)
    error_messages_list = []
    if error_value < 0xffff and error_value > 0:
        if error_value % 2 == 1:
            error_messages_list.append("蓄电池超压")
        error_value = error_value//2
        if error_value % 2 == 1:
            error_messages_list.append("蓄电池未接")
        error_value = error_value//2
        if error_value % 2 == 1:
            error_messages_list.append("光伏阵列过压")
        error_value = error_value//2
        if error_value % 2 == 1:
            error_messages_list.append("控制器短路")
        error_value = error_value//2
        if error_value % 2 == 1:
            error_messages_list.append("充电过流")
        error_value = error_value//2
        if error_value % 2 == 1:
            error_messages_list.append("控制器过热")
        error_value = error_value//2
        if error_value % 2 == 1:
            error_messages_list.append("蓄电池过热")
        error_value = error_value//2
        if error_value % 2 == 1:
            error_messages_list.append("输出过载")
        error_value = error_value//2
        if error_value % 2 == 1:
            error_messages_list.append("存储器读写错误")
        error_value = error_value//2
        if error_value % 2 == 1:
            error_messages_list.append("未知错误1")
        error_value = error_value//2
        if error_value % 2 == 1:
            error_messages_list.append("未知错误2")
        error_value = error_value//2
        if error_value % 2 == 1:
            error_messages_list.append("蓄电池欠压")
        error_value = error_value//2
        if error_value % 2 == 1:
            error_messages_list.append("控制器温度传感器失效")
        error_value = error_value//2
        if error_value % 2 == 1:
            error_messages_list.append("蓄电池温度传感器失效")
        error_value = error_value//2
        if error_value % 2 == 1:
            error_messages_list.append("光伏阵列欠压")
        error_value = error_value//2
        if error_value % 2 == 1:
            error_messages_list.append("未知错误3")
    return error_messages_list


def get_sensor_data() -> dict:
    port = sensor_config("serial_port", "")
    dev_addr = controller_config.get("device_addr", -1)
    for n in range(3):
        recived_data = send_command(
            port, dev_addr, GET_SENSOR_DATA_COMMAND, [0x00, 0x00], 3)
        if len(recived_data) > 0:
            break
        time.sleep(1)
    if len(recived_data) == 0:
        return {}
    # 将bytes list 转为控制器数据字典
    data_frame_dict = {}
    for offset in range(3):
        data_frame_dict['0x{:02X}'.format(
            0x0000+offset)] = byteslist_to_number(recived_data[3+offset*2:3+offset*2+2])
    data_dict = {}
    data_dict["sensor_temperature"] = \
        float('%0.2f' % (data_frame_dict.get("0x0000", 0)/100))
    data_dict["sensor_humidity"] = \
        float('%0.2f' % (data_frame_dict.get("0x0000", 0)/100))
    return data_dict


def search_device(command_code: int, addr: list, dev_addr=-1) -> dict:
    logging.debug(
        f"search device with command '{'0x{:02X}'.format(command_code)}', address: {byteslist_to_stringlist(addr)}")
    rtn = {}
    port_list = get_port_list()
    # port_list=list( p. for p in get_port_list()))
    dev_addr_list = []
    retry_times = 3
    if len(port_list) > 0:
        for port in port_list:
            for b_rate in BAUD_RATE_LIST:
                if dev_addr < 0:
                    dev_addr_list = range(254)
                else:
                    dev_addr_list = [dev_addr]
                for dev_addr in dev_addr_list:
                    for i in range(1, retry_times):
                        receive = send_command(
                            port, dev_addr, command_code, addr, 1, DEFAULT_DATA_UNIT, b_rate, 1)
                        if len(receive) > 0:
                            rtn["serial_port"] = port
                            rtn["device_addr"] = dev_addr
                            logging.info(
                                f"device '{'0x{:02X}'.format(dev_addr)}' found at port '{port}'")
                            return rtn
    return rtn


def controller_data_loop(ali_thing: aliyun_iot.AliThing, controller_interval: int):
    # 控制器数据循环
    global controller_data_dict
    start_time = time.time()
    while True:
        now_stamp = time.time()
        if int(now_stamp-start_time) % controller_interval == 0:
            controller_data_dict = get_controller_data()
            controller_data_dict.update(  # 追加processor_temp的数据
                {"processor_temp": get_system_temperature()})
            ali_thing.post_property(controller_data_dict)
        time.sleep(1)


def start_controller_data_loop(ali_thing: aliyun_iot.AliThing, controller_interval: int):
   # 启动controller loop
    if load_controller_config():
        # 加载配置文件成功
        # 加载 controller custom数据
        controller_custom_data_dict = get_controller_custom_data()
        if controller_custom_data_dict == {}:
            # 加载数据未成功
            logging.warning("controller custom data read faild")
        else:
            # 加载数据成功
            controller_custom_data_file_name = "./data/controller_custom_data.json"
            try:
                with open(controller_custom_data_file_name, 'w', encoding='UTF-8') as controller_costom_data_file:
                    json.dump(controller_custom_data_dict,
                              controller_costom_data_file,  ensure_ascii=False, indent=2)
            except:
                logging.warning(
                    f"controller custom data file '{controller_custom_data_file_name}' write fail.")
        # 开启loop
        controller_loop_thread = threading.Thread(
            target=controller_data_loop, args=(ali_thing, controller_interval))
        controller_loop_thread.setDaemon(True)
        controller_loop_thread.start()
    else:
        # 加载配置文件失败
        logging.critical(f"controller config 加载失败.")
        sys.exit()


def sensor_data_loop(ali_thing: aliyun_iot.AliThing, sensor_interval: int):
    # 传感器数据循环
    global sensor_data_dict
    start_time = time.time()
    while True:
        now_stamp = time.time()
        if int(now_stamp-start_time) % sensor_interval == 0:
            sensor_data_dict = get_sensor_data()
            ali_thing.post_property(sensor_data_dict)
        time.sleep(1)


def start_sensor_data_loop(ali_thing: aliyun_iot.AliThing, sensor_interval: int):
    # 启动sensor loop
    if load_sensor_config():
        # 加载配置文件成功
        # 开启loop
        sensor_loop_thread = threading.Thread(
            target=sensor_data_loop, args=(ali_thing, sensor_interval))
        sensor_loop_thread.setDaemon(True)
        sensor_loop_thread.start()
    else:
        # 加载配置文件失败
        logging.error(f"sensor config 加载失败.")


if __name__ == "__main__":
    print(load_controller_config())
    pass
