import crc
import requests

# # data = [0x06, 0x03, 0x10, 0x24, 0x00, 0x01, 0xc1]
# data = [0x06, 0x04, 0x10, 0x00, 0x00, 0x1D]
#
# # data = b'\x06\x03\x10\x24\x00\x01\xc1'
# full_data = crc.append_crc(data)
# print(crc.get_hex_string(full_data))

url = "http://api.tlink.io/oauth/token?grant_type=password&amp;username=a7e9b20018564381a697ad430c589f08&amp;password=c998bf81d1c046b9b9a6c9a3eba207c7"
response = requests.post(url)
pass