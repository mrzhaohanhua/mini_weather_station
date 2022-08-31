import crcmod


def append_crc(data: list, reverse: bool = True) -> list:
    """
    在数据后追加2字节crc校验
    :param data: 数据列表
    :param reverse: crc校验值格式，true:高位在前，false:低位在前
    :return: 含有crc校验值的数据列表
    """
    return data + get_modbus_crc(data, reverse)


def get_modbus_crc(data: list, reverse: bool = True) -> list:
    """
    按照modbus协议使用的crc算法计算crc校验值
    :param data: 数据列表
    :param reverse: crc校验值格式，true:高位在前，false:低位在前
    :return: crc数值列表
    """
    data_bytes = bytes(data)  # 将数据列表转为bytes
    modbus_crc_func = crcmod.predefined.mkPredefinedCrcFun(
        'modbus')  # 调用crcmod中的函数进行计算
    crc_value = modbus_crc_func(data_bytes)
    if reverse:
        # 低位在前，高位在后
        return [crc_value % 0x100, int(crc_value / 0x100)]
    else:
        # 高位在前，低位在后
        return [int(crc_value / 0x100), crc_value % 0x100]


def crc_check(data: list, crc_reverse: bool = True) -> bool:
    """
    检查数据最后2字节是否为前序数据的crc校验码
    :param data: 要娇艳的数据列表
    :return: 返回true 或者 false
    """
    list1=data[-2:]
    list2=data[:-2]
    list2_crc=get_modbus_crc(list2)
    return data[-2:] == get_modbus_crc(data[:-2])


def get_hex_string(data: list) -> list:
    """
    数据转为十六进制字符串列表
    :param data:数据列表
    :return:返回字符串列表
    """
    rtn = []
    for d in data:
        rtn.append(hex(d))
    return rtn
