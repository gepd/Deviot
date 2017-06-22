from time import sleep
from socket import inet_ntoa
from .zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf

class MDNSBrowser:
    """
    Class for zeroconf multicast DNS service discovery of arduino (esp)
    instances in local network

    The list will have the following format:
    [{
        'address': 'ip string', 
        'port': 'port string', 
        'weight': 'weight string', 
        'priority': 'priority string'
        'board': 'board string',
        'ssh_upload' 'yes/no',
        'auth_upload': 'yes/no'
    }]
    """

    def __init__(self):
        self._zeroconf = None
        self._browser = None
        self.services = []

    def start(self):
        """Start zeroconf
        
        Starts to browsing in the arduino instance
        """
        self._zeroconf = Zeroconf()
        self._browser = ServiceBrowser(self._zeroconf, '_arduino._tcp.local.',
                                       handlers=[self.on_service_state_change])
        sleep(0.15)
        self._zeroconf.close()

    def on_service_state_change(self, zeroconf, service_type, name, state_change):
        """Service state change

        Runs every time service in MDNS changes state(removed, added, modified).
        On service added, the device will be add to self. services
        """
        if(state_change is ServiceStateChange.Added):
            device = {}

            info = zeroconf.get_service_info(service_type, name)
            if(info):
                device['address'] = inet_ntoa(info.address)
                device['port'] = info.port
                device['weight'] = info.weight
                device['priority'] = info.priority
                for key, value in info.properties.items():
                    key = key.decode("utf-8")
                    value = value.decode("utf-8")
                    device[key] = value

                self.services.append(device)