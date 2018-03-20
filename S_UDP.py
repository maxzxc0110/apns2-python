# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys,json,socket,time,random,logging,os

from hyper import HTTP20Connection, tls
def make_response(r):
    try:
        info = r.read()
    except Exception , e:
        print Exception,":",e
                            
    code = r.status
    return code,info

def writeLog(info):
    logging.basicConfig(filename='/yourpath/py.log',level=logging.INFO)   #接口调用日志输出到py.log
    logging.info('[Time]:'+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+':'+info)
    #printf("[Time]:%Y-%m-%d %H:%M:%S : %s" % (time.localtime(), info)

def micro():
    return float(time.time())
sys.stdout = open('/yourpath/trace.log', 'a+')  #把异常捕获重定向到trace.log
sys.stderr = open('/yourpath/error.log', 'a+')  #把py错误日志输出到error.log
d = {}
Lport = 9090
host = "0.0.0.0"
s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 

s.bind((host,Lport))

# 第一次调用，连接apns，连接成功，把连接句柄存入数组
# 第二次调用，在数组里找句柄，如果句柄可用，复用句柄发送数据
# 第N次调用，重复第二步，如果句柄失效，重新再连接一次，并存入数组

print 'bind to the ' ,host ,Lport
while True:
        writeLog('PUSH START~~~~~~~~~~~~~~~~')
        try:
            data,addr = s.recvfrom(1024) 
        except Exception , e:
            print Exception,":",e
            continue
            
        writeLog("The receiving parameters are complete:"+data)

        start = micro()

        try:
            dirt    = eval(data)
        except Exception , e:
            print Exception,":",e
            s.sendto('400|{"reason":"IllegalParam"}|0.0',addr)   #参数异常
            writeLog('400|{"reason":"IllegalParam"}|0.0')
            continue
        else:
            if len(dirt) != 6:
                s.sendto('500|{"reason":"paramMiss"}|0.0',addr)  #参数缺少
                writeLog('500|{"reason":"paramMiss"}|0.0')
                continue

            sound   = dirt['sound']
            cert    = dirt['cert']
            remark  = dirt['remark']
            token   = dirt['token']
            topic   = dirt['topic']
            message = dirt['message']

            isfile = os.path.isfile('/yourpath/'+cert)
            if isfile is False:
                s.sendto('400|{"reason":"certNotExit"}|0.0',addr)   #证书不存在
                writeLog('400|{"reason":"certNotExit"}|0.0')
                continue


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
                    # "Connection":"Keep-Alive",
                    }

            connName = cert.replace('.pem','')
            one = micro()
            writeLog("The receiving parameters are complete,TIME:"+str(one-start));
            if connName in d:
                two = micro()
                try:
                    d[connName].request('POST', '/3/device/%s' % token, body=json.dumps(payload), headers=headers)   #为了防止连接过期
                except Exception , e:
                    print Exception,":",e
                    try:
                        d[connName] = HTTP20Connection('api.push.apple.com:443', ssl_context=tls.init_context(cert='/yourpath/'+cert),cert_password=yourpasswd)
                    except Exception , e:
                        print Exception,":",e
                        s.sendto('404|{"reason":"connectErr"}|0.0',addr)  #无法连接apns，通常是因为证书失效
                        writeLog('404|{"reason":"connectErr222"}|0.0')
                        continue
                    else:
                        writeLog("Connection handle is completed 222, Time:"+str(two-one))
                        try:
                            d[connName].request('POST', '/3/device/%s' % token, body=json.dumps(payload), headers=headers)
                            resp = d[connName].get_response()
                        except Exception , e:
                            print Exception,":",e
                            continue
                            
                        writeLog("Send apns finished,time222:"+str(micro()-one))
                        #data = resp.read()
                        try:
                            status,data =  make_response(resp)
                        except Exception , e:
                            print Exception,":",e
                            continue
                            
                        if data=='':
                           data = '{"reason":"sucess"}'
                           
                    continue 
                        
                else:
                    try:
                        resp = d[connName].get_response()
                    except Exception , e:
                        print Exception,":",e
                        continue
                        
                    writeLog("Send apns finished,time:"+str(two-one))
                    #data = resp.read()
                    
                    try:
                        status,data =  make_response(resp)
                    except Exception , e:
                        print Exception,":",e
                        continue
                            
                    if data=='':
                       data = '{"reason":"sucess"}'

            else:
                two = micro()
                try:
                    d[connName] = HTTP20Connection('api.push.apple.com:443', ssl_context=tls.init_context(cert='/yourpath/'+cert),cert_password=yourpasswd)
                except Exception , e:
                    print Exception,":",e
                    s.sendto('404|{"reason":"connectErr"}|0.0',addr)  #无法连接apns，通常是因为证书失效
                    writeLog('404|{"reason":"connectErr"}|0.0')
                    continue
                else:
                    writeLog("Connection handle is completed, Time:"+str(two-one))
                    try:
                        d[connName].request('POST', '/3/device/%s' % token, body=json.dumps(payload), headers=headers)
                        resp = d[connName].get_response()
                    except Exception , e:
                        print Exception,":",e
                        continue

                    writeLog("Send apns finished,time:"+str(micro()-one))
                    #data = resp.read()
                    try:
                        status,data =  make_response(resp)
                    except Exception , e:
                        print Exception,":",e
                        continue
                            
                    if data=='':
                       data = '{"reason":"sucess"}'
  
            elapsed = (micro() - start)
            writeLog(str(status)+'|'+data+'|'+str(elapsed))
            s.sendto(str(status)+'|'+data+'|'+str(elapsed),addr)
        
        writeLog('PUSH END~~~~~~~~~~~~~~~~')
        writeLog("PUSH TIME="+str(elapsed))
        if data=='exit':
            print('***recv exit!!!')
            break
    
s.close

