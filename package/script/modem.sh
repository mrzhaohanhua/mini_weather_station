#!/bin/sh

#本脚本用于启动modem

echo "--------------------" >> /home/pi/wvdial_log.txt
date >> /home/pi/wvdial_log.txt

HW_OK=0
TIM=1

while [[ $HW_OK -ne 1 && && &TIM -le 10 ]]
do
echo $TIM >> /home/pi/wvdial_log.txt
lsusb >> /home/pi/wvdial_log.txt
if sudo wvdial hw >> /home/pi/wvdial_log.txt 2>&1
then
    HW_OK=1
    echo "OK" >> /home/pi/wvdial_log.txt
else
    echo "false" >> /home/pi/wvdial_log.txt
fi
TIM=$(($TIM+1))
sleep 10
done