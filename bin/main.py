import aliyun_iot
import json


def load_config():
    global sensor_interval
    global controller_interval
    config = {}
    config_file_name = "./data/config.json"
    try:
        with open(config_file_name, 'r', encoding='UTF-8') as config_file:
            config = json.load(config_file)
    except:
        pass

    sensor_interval = config.get("sensor_interval", 600)
    controller_interval = config.get("controller_interval", 60)

    if sensor_interval < 10 or isinstance(sensor_interval, int) == False:
        sensor_interval = 600
    if controller_interval < 10 or isinstance(controller_interval, int) == False:
        controller_interval = 60

    new_config = {
        "sensor_interval": sensor_interval,
        "controller_interval": controller_interval
    }
    if new_config != config or config == {}:
        try:
            with open(config_file_name, 'w', encoding='UTF-8') as config_file:
                json.dump(new_config, config_file, indent=2)
        except:
            pass


if __name__ == "__main__":
    """
    程序入口
    """
    # 配置参数
    sensor_interval: int  # 传感器读取时间间隔,秒
    controller_interval: int  # 控制器读取时间间隔,秒
    load_config()
    ali_thing = aliyun_iot.load_ali_thing()  # 加载阿里云设备模型
    pass
