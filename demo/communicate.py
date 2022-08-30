import json


def byte_to_int(data: list) -> int:
    if len(data) == 2:
        return data[0] * 0x100 + data[1]
    elif len(data) == 4:
        return data[0] * 0x1000000 + data[1] * 0x10000 + data[2] * 0x100 + data[3]
    else:
        return None


def mppt_data_to_dict(data: list) -> dict:
    rtn = {}
    try:
        mppt_data_dict_file = open('..\\data\\mppt_data.json', 'r')
        rtn = json.load(mppt_data_dict_file)
        pt = 0
        rtn['软件版本号'] = byte_to_int(data[pt: pt + 2])
        pt += 2
        rtn['光伏板电压'] = byte_to_int(data[pt: pt + 2]) * 0.1
        pt += 2
        rtn['蓄电池电压'] = byte_to_int(data[pt: pt + 2]) * 0.1
        pt += 2
        rtn['A通道电流'] = byte_to_int(data[pt: pt + 2]) * 0.1
        pt += 2
        rtn['B通道电流'] = byte_to_int(data[pt: pt + 2]) * 0.1
        pt += 2
        rtn['充电总电流'] = byte_to_int(data[pt: pt + 2]) * 0.1
        pt += 2
        rtn['充电器温度'] = byte_to_int(data[pt: pt + 2])
        pt += 2
        rtn['充电功率'] = byte_to_int(data[pt: pt + 2]) * 0.1
        pt += 2
        rtn['放电功率'] = byte_to_int(data[pt: pt + 2]) * 0.1
        pt += 2
        rtn['蓄电池容量'] = byte_to_int(data[pt: pt + 2])
        pt += 2
        rtn['充电状态'] = byte_to_int(data[pt: pt + 2])
        pt += 2
        rtn['负载状态'] = byte_to_int(data[pt: pt + 2])
        pt += 2
        rtn['放电电流'] = byte_to_int(data[pt: pt + 2]) * 0.1
        pt += 2
        rtn['过放次数'] = byte_to_int(data[pt: pt + 2])
        pt += 2
        rtn['充电总瓦时数'] = byte_to_int(data[pt: pt + 4]) * 0.1
        pt += 4
        rtn['放电总瓦时数'] = byte_to_int(data[pt: pt + 4]) * 0.1
        pt += 4
        rtn['蓄电池温度'] = byte_to_int(data[pt: pt + 2])
        pt += 2
        rtn['故障码'] = byte_to_int(data[pt: pt + 2])
        pt += 2
        rtn['控制器电压等级'] = byte_to_int(data[pt: pt + 2])
        pt += 2
        rtn['PV备采电压'] = byte_to_int(data[pt: pt + 2])
        pt += 2
        rtn['控制器电流等级'] = byte_to_int(data[pt: pt + 2])
        pt += 2
        rtn['蓄电池组串数'] = byte_to_int(data[pt: pt + 2])
        pt += 2
        rtn['电池类型'] = byte_to_int(data[pt: pt + 2])
        pt += 2
        rtn['充电开关状态'] = byte_to_int(data[pt: pt + 2])
        pt += 2
        rtn['风扇运行状态'] = byte_to_int(data[pt: pt + 2])
        pt += 2
        rtn['蓄电池温度补偿电压点'] = byte_to_int(data[pt: pt + 2])
        pt += 2
        rtn['负载开关状态'] = byte_to_int(data[pt: pt + 2])
    except FileNotFoundError:
        pass
    return rtn
