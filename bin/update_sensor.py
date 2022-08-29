import json

import requests


def upload_tlink():
    post_data = {}
    post_data["userId"] = tlink_connection.get("user_id", "")
    post_data["deviceNo"] = tlink_connection.get("device_no", "")
    post_data["sensorDatas"] = [{tlink_connection.get("sensor_no", None).get("温度传感器", ""): 35.5}]
    try:
        url = tlink_connection.get("http_access_point", "")
        headers = {"Content-Type": "application/json", "Authorization": "Basic 7d321843-17a3-4f02-91e4-d42004b68da1"}
        response = requests.post(url, json=post_data, headers=headers)
        response_string = str(response.content, 'utf-8')
        response_dict: dict = eval(response_string)
        result = response_dict.get('result', 0)
        if result != 1:
            print(f"error: {response_dict.get('message', 'unknown error')}")
        pass

    except requests.exceptions.ConnectionError:
        print("connection error")


thingscloud_connection = {}
tlink_connection = {}
with open("..//data//connections.json", "r", encoding='UTF-8') as connection_config_file:  # 读取连接配置文件
    connection_config_list = json.load(connection_config_file)
    for con in connection_config_list:
        con_platform = con.get("platform", "")
        if con_platform == "ThingsCloud":
            thingscloud_connection = con.get("connection", None)
        elif con_platform == "TLink":
            tlink_connection = con.get("connection", None)
        else:
            pass
upload_tlink()

# def upload_data(data: dict):
#     """
#     上传数据
#     :param data:字典格式的数据
#     :return:
#     """
#
#
# def upload_value(value_name: str, value):
#     """
#     上传数据
#     :param value_name:属性标识符
#     :param value:属性值
#     :return:
#     """
#     try:
#         connection_file = open('../data/connections.json', 'r')  # 读取连接配置文件
#         connection_config: dict  # 定义连接配置的字典
#         connection_config = json.load(connection_file)  # 将配置文件读取到字典
#         http_access_point = connection_config.get('http_access_point', '')
#         access_token = connection_config.get('access_token', '')
#         project_key = connection_config.get('project_key', '')
#         url: str = f"{http_access_point}/device/v1/{access_token}/attributes"
#         headers = {"Content-Type": "application/json", "Project-Key": project_key}
#         response = requests.post(url, json={value_name: value}, headers=headers)
#         response_string = str(response.content, 'utf-8')
#         response_dict: dict = eval(response_string)
#         result = response_dict.get('result', 0)
#         if result != 1:
#             print(f"error: {response_dict.get('message', 'unknown error')}")
#         pass
#     except FileNotFoundError:
#         print("error: connections.json file not found")
#     except requests.exceptions.ConnectionError:
#         print("error: connection error")
