#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import json
import socket
import time
import random
import logging
import os
import threadpool
import threading
from hyper import HTTP20Connection, tls

def make_response(r):
    info = r.read()
    code = r.status
    return code,info

def writeLog(info):
    global path
    logging.basicConfig(filename=path+'log.log',level=logging.INFO)
    logging.info('[Time]:'+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+':'+info)

def micro():
    return float(time.time())


def sendApns2(cert,token,payload,headers,conn):
    conn.request('POST', '/3/device/%s' % token, body=json.dumps(payload), headers=headers)
    resp = conn.get_response()
    return make_response(resp)

def getParms(data):
    try:
        dirt    = eval(data)
        if len(dirt) == 6:
            sound   = dirt['sound']
            cert    = dirt['cert']
            remark  = dirt['remark']
            token   = dirt['token']
            topic   = dirt['topic']
            message = dirt['message']
            ParamErr    = False
        else:
            ParamErr    = True
    except:
        ParamErr    = True
    if ParamErr is False:
        return ParamErr,sound,cert,remark,token,topic,message
    else:
        return ParamErr

    

def getPayloadAndHeaders(message,sound,remark,topic):
    payload = {
                    'aps': 
                    {
                        'alert': message,
                        'sound': sound,
                        'badge': 1,
                        'remark':remark,
                    }
              }
    headers = {
                    "apns-topic": topic,
                    "Content-type": "application/x-www-form-urlencoded",
                    "Accept": "text/plain",
                    "Connection":"Keep-Alive",
              }
    return payload,headers


def send(data,addr,s):
        global  d
        global path
        start = micro()
        writeLog("param="+data)
        if getParms(data) is True:
            # continue
            return
        else:
            ParamErr,sound,cert,remark,token,topic,message = getParms(data)
        isfile = os.path.isfile(path+cert)
        if isfile is False:
            s.sendto('400|{"reason":"certNotExit"}|0.0',addr)   #证书不存在
            writeLog('400|{"reason":"certNotExit"}|0.0')
            # continue
            return
        payload,headers = getPayloadAndHeaders(message,sound,remark,topic)        
        connName = cert.replace('.pem','')
        try:
            if connName in d:
                writeLog("复用链接:"+connName)
                d[connName].request('POST', '/3/device/%s' % token, body=json.dumps(payload), headers=headers)
                resp = d[connName].get_response()
                status,data =  make_response(resp)
            else:
                writeLog("开启一个新链接")
                d[connName] = HTTP20Connection('api.push.apple.com:443', ssl_context=tls.init_context(cert=path+cert),cert_password=123456)
                conn = d[connName]
                status,data = sendApns2(cert,token,payload,headers,conn)
            if data=='':
                data = 'sucess'
        except:
            del d[connName]
            writeLog("清空链接:"+connName)
            status = 500
            data = "apns2 connect error"
            s.close
        elapsed = (micro() - start)
        writeLog(str(status)+'|'+data+'|'+str(elapsed))
        s.sendto(str(status)+'|'+data+'|'+str(elapsed),addr)
        writeLog('PUSH END~~~~~~~~~~~~~~~~')
        writeLog("PUSH TIME="+str(elapsed))

def print_result():
    pass


def main():
    Lport = 9090
    host = "0.0.0.0"
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
    s.bind((host,Lport))
    print 'bind to the ' ,host ,Lport
    pool = threadpool.ThreadPool(10)#开启10个线程的线程池
    while True:
        writeLog('PUSH START~~~~~~~~~~~~~~~~')
        data,addr = s.recvfrom(1024) 
        dct1 = {'data':data,'addr':addr,'s':s}
        param = [(None, dct1)]
        requests = threadpool.makeRequests(send, param, print_result)
        [pool.putRequest(req) for req in requests]
        # pool.wait()
        # send(data,addr,s)



if __name__ == '__main__':
    path = "/home/goolink/apns2/"
    sys.stderr = open(path+'error.log', 'a+')  #把py错误日志输出到error.log
    d = {} #链接字典
    main()
