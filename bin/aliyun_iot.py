from linkkit import linkkit
import logging
import threading
import json
import sys
import time


class AliThing(object):
    """
    阿里Iot设备类
    """

    def __init__(self,  product_key, device_name, device_secret, host_name="cn-shanghai"):
        global property_upload_on_duty
        global property_upload_buffer
        property_upload_on_duty = False
        property_upload_buffer = {}
        self.__linkkit = linkkit.LinkKit(  # 连接参数
            host_name=host_name,
            product_key=product_key,
            device_name=device_name,
            device_secret=device_secret)
        self.__linkkit.thing_setup()
        self.__linkkit.on_device_dynamic_register = self.on_device_dynamic_register
        self.__linkkit.on_connect = self.on_connect
        self.__linkkit.on_disconnect = self.on_disconnect
        self.__linkkit.on_topic_message = self.on_topic_message
        self.__linkkit.on_subscribe_topic = self.on_subscribe_topic
        self.__linkkit.on_unsubscribe_topic = self.on_unsubscribe_topic
        self.__linkkit.on_publish_topic = self.on_publish_topic
        self.__linkkit.on_thing_enable = self.on_thing_enable
        self.__linkkit.on_thing_disable = self.on_thing_disable
        self.__linkkit.on_thing_event_post = self.on_thing_event_post
        self.__linkkit.on_thing_prop_post = self.on_thing_prop_post
        self.__linkkit.on_thing_prop_changed = self.on_thing_prop_changed
        self.__linkkit.on_thing_call_service = self.on_thing_call_service
        self.__linkkit.on_thing_raw_data_post = self.on_thing_raw_data_post
        self.__linkkit.on_thing_raw_data_arrived = self.on_thing_raw_data_arrived
        self.__call_service_request_id = 0
        loop_thread = threading.Thread(target=self.start_loop)
        loop_thread.setDaemon(True)
        loop_thread.start()

    def on_device_dynamic_register(self, rc, value, userdata):
        if rc == 0:
            logging.debug("dynamic register device success, value:" + value)
        else:
            logging.debug("dynamic register device fail, message:" + value)

    def on_connect(self, session_flag, rc, userdata):
        logging.debug("on_connect:%d,rc:%d,userdata:" % (session_flag, rc))

    def on_disconnect(self, rc, userdata):
        logging.debug("on_disconnect:rc:%d,userdata:" % rc)

    def on_topic_message(self, topic, payload, qos, userdata):
        logging.debug("on_topic_message:" + topic + " payload:" +
                      str(payload) + " qos:" + str(qos))
        pass

    def on_subscribe_topic(self, mid, granted_qos, userdata):
        logging.debug("on_subscribe_topic mid:%d, granted_qos:%s" %
                      (mid, str(','.join('%s' % it for it in granted_qos))))
        pass

    def on_unsubscribe_topic(self, mid, userdata):
        logging.debug("on_unsubscribe_topic mid:%d" % mid)
        pass

    def on_publish_topic(self, mid, userdata):
        logging.debug("on_publish_topic mid:%d" % mid)

    def on_thing_prop_changed(self, params, userdata):
        logging.debug("on_thing_prop_changed params:" + str(params))

    def on_thing_enable(self, userdata):
        logging.debug("on_thing_enable")

    def on_thing_disable(self, userdata):
        logging.debug("on_thing_disable")

    def on_thing_event_post(self, event, request_id, code, data, message, userdata):
        logging.debug("on_thing_event_post event:%s,request id:%s, code:%d, data:%s, message:%s" %
                      (event, request_id, code, str(data), message))

    def on_thing_prop_post(self, request_id, code, data, message, userdata):
        global property_upload_on_duty
        global property_upload_buffer

        logging.debug("on_thing_prop_post request id:%s, code:%d, data:%s message:%s" %
                      (request_id, code, str(data), message))
        property_upload_on_duty = False
        property_upload_buffer = {}

    def on_thing_raw_data_arrived(self, payload, userdata):
        logging.debug("on_thing_raw_data_arrived:%s" % str(payload))

    def on_thing_raw_data_post(self, payload, userdata):
        logging.debug("on_thing_raw_data_post: %s" % str(payload))

    def on_thing_call_service(self, identifier, request_id, params, userdata):
        logging.debug("on_thing_call_service identifier:%s, request id:%s, params:%s" %
                      (identifier, request_id, params))
        self.__call_service_request_id = request_id

    def post_property(self, property_dict: dict) -> bool:
        # 设置属性
        global property_upload_on_duty
        global property_upload_buffer
        retry_times = 0
        max_retry_times = 3
        while True:
            if property_upload_on_duty:
                if retry_times > max_retry_times:
                    logging.warning(
                        f"max retry times {max_retry_times} reached, property dict will drop.")
                    break
                logging.info("previous upload session is processing.")
                time.sleep(1)
                retry_times += 1
            else:#property_upload_on_duty为False
                property_upload_buffer.update(property_dict) #向buffer中增加数值
                break

    # def set_property(self, property_data: dict):
    #     global post_property_buff
    #     post_property_buff = property_data

    def start_loop(self):
        global link_disconnect
        global property_upload_on_duty
        global property_upload_buffer

        self.__linkkit.connect_async()
        while True:
            if self.__linkkit.check_state() == linkkit.LinkKit.LinkKitState.CONNECTED:
                break
            elif self.__linkkit.check_state() == linkkit.LinkKit.LinkKitState.DISCONNECTED:
                sys.exit()
        link_disconnect = False
        while True:
            time.sleep(1)
            if link_disconnect:
                sys.exit()
            if property_upload_buffer != {}:
                # buffer中有数据，开始上传
                property_upload_on_duty = True
                logging.debug(f"Post data {property_upload_buffer}")
                self.__linkkit.thing_post_property(property_upload_buffer)


def load_ali_thing() -> AliThing:
    # 读取连接配置文件
    global ali_thing
    ali_thing_config = {}
    ali_thing_config_file_name = "./data/ali_thing_config.json"
    logging.debug(f"Load AliThing config file '{ali_thing_config_file_name}'")
    try:
        with open(ali_thing_config_file_name, 'r', encoding='UTF-8') as ali_thing_config_file:
            ali_thing_config = json.load(ali_thing_config_file)  # json文件转字典
    except FileNotFoundError:
        logging.warning(
            f"AliThing config file '{ali_thing_config_file_name}' not found.")

    host_name = ali_thing_config.get("host_name", "")
    product_key = ali_thing_config.get("product_key", "")
    device_name = ali_thing_config.get("device_name", "")
    device_secret = ali_thing_config.get("device_secret", "")

    if host_name == "":
        logging.debug(f"host_name is empty.")
        host_name = input("输入 host_name : [cn-shanghai] ")
        if host_name == "":
            host_name = "cn-shanghai"
        logging.debug(f"host_name set to '{host_name}'.")

    while product_key == "":
        logging.debug(f"product_key is empty.")
        product_key = input("输入 ProductKey : ")
        logging.debug(f"product_key set to '{product_key}'.")

    while device_name == "":
        logging.debug(f"device_name is empty.")
        device_name = input("输入 device_name : ")
        logging.debug(f"device_name set to '{device_name}'.")

    while device_secret == "":
        logging.debug(f"device_secret is empty.")
        device_secret = input("输入 device_secret : ")
        logging.debug(f"device_secret set to '{device_secret}'.")

    new_ali_thing_config = {
        "host_name": host_name,
        "product_key": product_key,
        "device_name": device_name,
        "device_secret": device_secret
    }
    if new_ali_thing_config != ali_thing_config or ali_thing_config == {}:
        logging.debug(
            f"AliThing config has been changed. Writing to '{ali_thing_config_file}'")
        try:
            with open(ali_thing_config_file_name, 'w', encoding='UTF-8') as ali_thing_config_file:
                json.dump(new_ali_thing_config,
                          ali_thing_config_file, indent=2)
        except:
            logging.warning(
                f"AliThing config file '{ali_thing_config_file}' write fail.")
            pass

    return AliThing(product_key, device_name, device_secret, host_name)


if __name__ == "__main__":
    pass
