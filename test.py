# your code goes here
class Server(object):

    def __init__(self, val):
        self.val = val

    def __call__(self):
        print 'Starting Server with val: ', self.val


class MyServer(Server):

    def __init__(self, wait, *args, **kwargs):
        self.wait = wait
        super(MyServer, self).__init__(*args, **kwargs)

    def __call__(self, app):
        print 'Wait time:', self.wait
        print 'App:', app
        return super(MyServer, self).__call__()


MyServer(10, 10)(app='hello')



import time
class MyServer(Server):

    def __init__(self, wait, *args, **kwargs):
        self.wait = wait
        super(MyServer, self).__init__(*args, **kwargs)

    def __call__(self):
        print 'Sleeping for {s} seconds before Start'.format(s=self.wait)
        time.sleep(self.wait)
        return super(MyServer, self).__call__()

import socket
import re
import sys


def check_server(address, port):
	s = socket.socket()
    i=0
    while i<10:
        try:
            s.connect((address, port))
            print "Connected to %s on port %s" % (address, port)
            return True
        except socket.error, e:
            time.sleep(1)
            print "Connection to %s on port %s failed: %s" % (address, port, e)
        i+=1


check_server('192.168.99.100',8080)
