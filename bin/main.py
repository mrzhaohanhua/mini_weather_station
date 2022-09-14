import sys
import aliyun_iot
import json
import time
import logging
import logging.config
# import sensor_module


def set_logging():
    #加载logging模块配置文件
    
    log_config = {}
    log_config_file_name = "./data/log_config.json"
    try:
        with open(log_config_file_name, 'r', encoding='UTF-8') as log_config_file:
            log_config = json.load(log_config_file)
    except FileNotFoundError:
        logging.critical("加载记录器配置文件失败.")
        exit()

    logging.config.dictConfig(log_config)


def load_config():  # 读取配置文件
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


def main(argv):
    global ali_thing
    set_logging()  # 配置日志记录器
    # 配置参数
    load_config()  # 加载程序配置
    ali_thing = aliyun_iot.load_ali_thing()  # 加载阿里云设备模型
    sensor_module.start_controller_data_loop(
        ali_thing, controller_interval)  # 开始控制器循环
    time.sleep(15)
    sensor_module.start_sensor_data_loop(ali_thing, sensor_interval)  # 开启传感器循环
    while True:
        time.sleep(10)


if __name__ == "__main__":
    main(sys.argv[1:])
