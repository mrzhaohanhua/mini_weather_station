# <font color=LightBlue>精能MPPT控制器</font>

## 1. 物理接口

>接口标准: RS485

>通讯方式: 异步串行

>波特率: 9600

每帧数据10位（包括1个起始位，8个数据位，1个停止位，无奇偶校验）

所有数据均是16进制无符号数

## 2. 通讯协议

采用标准MODBUS协议

ADDR: 本机地址（范围：`01H` - `FEH`），`FFH`为广播地址，设备默认地址为`06H`

### 2.1 读取当前运行参数

使用功能码`04H`

下发信息：

| 定义 | 地址 | 功能码 | 起始寄存器地址 | 寄存器个数 | CRC校验 |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 数据 | ADDR | 04H | 1000H | 001DH | CRC16 |
| 字节数 | 1 | 1 | 2 | 2 | 2 |

控制器返回信息：

| 定义 | 地址 | 功能码 | 返回数据字节数 | 返回数据 | CRC校验 |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 数据 | ADDR | 04H | 3AH | DATA | CRC16 |
| 字节数 | 1 | 1 | 1 | 58 | 2 |

