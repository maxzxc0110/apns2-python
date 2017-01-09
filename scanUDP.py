#!/usr/bin/python
# -*- coding: UTF-8 -*-
#一个监视UDP服务的脚本
import logging
import os
import time

def writeLog(info):
    logging.basicConfig(filename='/yourpath/UDP2.log',level=logging.INFO)
    logging.info('[Time]:'+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+':'+info)


com = "netstat -apn|grep 0.0.0.0:9090"
a = os.system(com)
if(a!=0):
   writeLog("The service crashed~")
   c = "python /yourpath/createDaemon_2.py"
   os.system(c)


   
 


