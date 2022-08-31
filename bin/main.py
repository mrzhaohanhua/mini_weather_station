import aliyun_iot
import json
import time
import logging
import logging.config


def set_logging():
    """
    加载logging模块配置文件
    """
    log_config = {}
    log_config_file_name = "./data/log_config.json"
    try:
        with open(log_config_file_name, 'r', encoding='UTF-8') as log_config_file:
            log_config = json.load(log_config_file)
    except FileNotFoundError:
        print("\n严重错误:无法找到日志记录器的配置文件.\n程序结束.")
        exit()

    logging.config.dictConfig(log_config)


def load_config():
    global sensor_interval
    global controller_interval
    config = {}
    config_file_name = "./data/config.json"  # 配置文件
    try:
        logging.debug(f"Open config file `{config_file_name}`")
        with open(config_file_name, 'r', encoding='UTF-8') as config_file:
            config = json.load(config_file)
        logging.debug("Config loaded")
    except FileNotFoundError:
        logging.warning(f"Config file '{config_file_name}' not found")
        pass

    sensor_interval = config.get("sensor_interval", 0)
    controller_interval = config.get("controller_interval", 0)

    if sensor_interval < 10 or isinstance(sensor_interval, int) == False:
        sensor_interval = 600
        logging.warning(
            f"sensor_interval less than 10 , RESET TO {sensor_interval}")
    if controller_interval < 10 or isinstance(controller_interval, int) == False:
        controller_interval = 60
        logging.warning(
            f"controller_interval less than 10 , RESET TO {controller_interval}")

    new_config = {
        "sensor_interval": sensor_interval,
        "controller_interval": controller_interval
    }
    if new_config != config or config == {}:
        logging.debug(
            f"Config has been changed. Writing to '{config_file_name}'")
        try:
            with open(config_file_name, 'w', encoding='UTF-8') as config_file:
                json.dump(new_config, config_file, indent=2)
        except:
            logging.warning(f"Config file '{config_file_name}' write fail.")
            pass


def main():
    set_logging()
    # 配置参数
    sensor_interval: int  # 传感器读取时间间隔,秒
    controller_interval: int  # 控制器读取时间间隔,秒
    load_config()
    ali_thing = aliyun_iot.load_ali_thing()  # 加载阿里云设备模型

    temp = 0
    humi = 0
    while True:
        time.sleep(2)
        ali_thing.set_property(
            {"sensor_temperature": temp, "sensor_humidity": humi})
        temp = temp+1
        humi = humi+1


if __name__ == "__main__":
    main()
