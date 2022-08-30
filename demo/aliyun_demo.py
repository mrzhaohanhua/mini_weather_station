import array
import time

from linkkit import linkkit

lk = linkkit.LinkKit(
    host_name="cn-shanghai",
    product_key="hlbjpeerN9E",
    device_name="dev0",
    device_secret="515de0553303fc45ca37b77a179fc7ca"
)

# lk.config_mqtt(port=1883, protocol="MQTTv311", transport="TCP", secure="TLS", keep_alive=60, clean_session=True,
#                max_inflight_message=20, max_queued_message=0, auto_reconnect_min_sec=1, auto_reconnect_max_sec=60,
#                cadata=None)

lk.connect_async()
lk.thing_setup()
while True:
    state = lk.check_state()
    print(state)
    if state == linkkit.LinkKit.LinkKitState.CONNECTED:
        break
    time.sleep(0.5)
print(f"lk.on_thing_prop_post : {lk.on_thing_prop_post}")

prop_data = {
    "sensor_temperature": 18
}
lk.thing_post_property(prop_data)
time.sleep(0.5)
print(f"lk.on_thing_prop_post : {lk.on_thing_prop_post}")
pass
