#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time,platform
import os

def createDaemon():
    # fork进程        
    try:
        if os.fork() > 0: os._exit(0)
    except OSError, error:
        print 'fork #1 failed: %d (%s)' % (error.errno, error.strerror)
        os._exit(1)    
    os.chdir('/')
    os.setsid()
    os.umask(0)
    try:
        pid = os.fork()
        if pid > 0:
            print 'Daemon PID %d' % pid
            os._exit(0)
    except OSError, error:
        print 'fork #2 failed: %d (%s)' % (error.errno, error.strerror)
        os._exit(1)

    os.system('python /yourpath/S_UDP.py')

if __name__ == '__main__': 
    if platform.system() == "Linux":
        createDaemon()
    else:
        os._exit(0)
