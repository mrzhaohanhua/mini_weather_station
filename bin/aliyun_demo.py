import array
import time

from linkkit import linkkit

lk = linkkit.LinkKit(
    host_name="cn-shanghai",
    product_key="hlbjpeerN9E",
    device_name="dev0",
    device_secret="515de0553303fc45ca37b77a179fc7ca"
)
lk.config_mqtt(port=1883, protocol="MQTTv311", transport="TCP", secure="TLS", keep_alive=60, clean_session=True,
               max_inflight_message=20, max_queued_message=0, auto_reconnect_min_sec=1, auto_reconnect_max_sec=60,
               cadata=None)

lk.connect_async()
for i in range(60):
    print(lk.check_state())
    time.sleep(1)
pass
