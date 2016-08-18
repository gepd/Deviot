import time
import socket
from zeroconf import ServiceBrowser, Zeroconf


class MyListener(object):

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        lista = {"server": str(info.server),
                 "ip": socket.inet_ntoa(info.address),
                 "properties": info.properties}
        print(lista)


zeroconf = Zeroconf()
listener = MyListener()
browser = ServiceBrowser(zeroconf, "_arduino._tcp.local.", listener)

time.sleep(0.2)
zeroconf.close()
