import time

from linkkit import linkkit

import json

if __name__ == "__main__":
    """
    程序入口
    """
    # 读取连接配置文件
    aliyun_connection = {}
    aliyun_link = None
    connection_file_name = "..//data//connections.json"
    with open(connection_file_name, 'r', encoding='UTF-8') as connection_config_file:
        connection_config_list = json.load(connection_config_file)
        for con in connection_config_list:
            con_platform = con.get("platform", "")
            if con_platform == "AliYun":
                # 连接AliYun平台
                connection_config = con.get("connection", None)
                host_name = connection_config.get("host_name", "")
                product_key = connection_config.get("product_key", "")
                device_name = connection_config.get("device_name", "")
                device_secret = connection_config.get("device_secret", "")
                aliyun_link = linkkit.LinkKit(host_name=host_name, product_key=product_key, device_name=device_name,
                                              device_secret=device_secret)
                # 使用MQTT协议连接
                aliyun_link.config_mqtt(port=1883, protocol="MQTTv311", transport="TCP", secure="TLS", keep_alive=60,
                                        clean_session=True,
                                        max_inflight_message=20, max_queued_message=0, auto_reconnect_min_sec=1,
                                        auto_reconnect_max_sec=60,
                                        cadata=None)
                aliyun_link.connect_async()  # 建立连接
    while True:
        aliyun_link_state = aliyun_link.check_state()
        print(aliyun_link_state)
        time.sleep(1)
        if aliyun_link_state == linkkit.LinkKit.LinkKitState.DISCONNECTED:
            break
        if aliyun_link_state == linkkit.LinkKit.LinkKitState.CONNECTED:
            print(f"on_thing_enable : {aliyun_link.on_thing_enable}")
            aliyun_link.on_thing_enable = True

            prop_data = {"sensor_humidity": 30.0, "sensor_temperature": 15.0}
            aliyun_link.thing_post_property(prop_data)
            time.sleep(1)
            print(f"on_thing_prop_post : {aliyun_link.on_thing_prop_post}")
