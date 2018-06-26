#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import json
import time
import logging
from hyper import HTTP20Connection, tls

def make_response(r):
    info = r.read()
    code = r.status
    return code,info

def writeLog(info):
    logging.basicConfig(filename='/path/cli.log',level=logging.INFO)
    logging.info('[Time]:'+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+':'+info)

def micro():
    return float(time.time())


def sendApns2(cert,token,payload,headers):
    conn = HTTP20Connection('api.push.apple.com:443', ssl_context=tls.init_context(cert='/path/'+cert),cert_password=123456)
    conn.request('POST', '/3/device/%s' % token, body=json.dumps(payload), headers=headers)
    resp = conn.get_response()
    return make_response(resp)


def main():
    start = micro()
    writeLog('报警开始~~~~~~~~~~~~~~~~')
    cert = sys.argv[1]
    token = sys.argv[2]
    topic = sys.argv[3]
    message = sys.argv[4]
    remark = sys.argv[5]
    sound = sys.argv[6]
    writeLog("parms:"+str(sys.argv))

    payload = {
    'aps': {
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

    status,data = sendApns2(cert,token,payload,headers)
    if data=='':
        data = 'sucess'
    elapsed = (micro() - start)
    print str(status)+'|'+data+'|'+str(elapsed)
    writeLog(str(status)+'|'+data+'|'+str(elapsed))
    writeLog('报警结束~~~~~~~~~~~~~~~~')
    writeLog("报警时间="+str(elapsed))





if __name__ == '__main__':
    
    main()

    



