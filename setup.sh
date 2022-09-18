#!/bin/bash

#=============================================
# System Required :
# Description :
# Author : Zhao Hanhua
#=============================================

#clear
clear
#验证是否有root权限
if ['id -u' -ne 0]; then
    exit
fi
