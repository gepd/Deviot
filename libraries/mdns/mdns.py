from time import sleep
from socket import inet_ntoa
from .zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf

current_services = {}
count_services = {}

class MDNSBrowser:
    """
    Class for zeroconf multicast DNS service discovery of arduino (esp)
    instances in local network
    """

    def __init__(self):
        global count_services
        global current_services

        self._zeroconf = None
        self._browser = None
        self.temp_addresses = []

    def start(self):
        """Start zeroconf
        
        Starts to browsing in the arduino instance
        """
        try:
            self._zeroconf = Zeroconf()
        except:
            # not connected
            return

        self._browser = ServiceBrowser(self._zeroconf, '_arduino._tcp.local.',
                                       handlers=[self.on_service_state_change])
        sleep(0.20)
        self._zeroconf.close()
        self.service_check()

    def on_service_state_change(self, zeroconf, service_type, name, state_change):
        """Service state change

        Runs every time service in MDNS changes state(removed, added, modified).
        On service added, the device will be add to self. services

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
        if(state_change is ServiceStateChange.Added):
            device = {}

            info = zeroconf.get_service_info(service_type, name)
            if(info):
                address = inet_ntoa(info.address)
                device['address'] = address
                device['port'] = info.port
                device['weight'] = info.weight
                device['priority'] = info.priority
                for key, value in info.properties.items():
                    key = key.decode("utf-8")
                    value = value.decode("utf-8")
                    device[key] = value

                count_services[address] = 0
                current_services[address] = device
                self.temp_addresses.append(address)

    def service_check(self):
        """Check Services
        
        Some times zeroconf can not see a device that was previously connected.
        With the use of two global variables, it will stop to show a device only
        if it is not found the number of time in the "threshold" variable.
        """
        threshold = 8

        counter = count_services.keys()
        removed = list(set(counter) - set(self.temp_addresses))

        for address in removed:
            count_services[address] = count_services[address] + 1

        from copy import deepcopy

        temp_count = deepcopy(count_services)
        for key, value in temp_count.items():
            if(value >= threshold):
                del count_services[key]
                del current_services[key]

    def formated_list(self):
        """List of services
        
        Returns only the neccessary data to work with the plugin
        
        Returns:
            list -- board id and addres (ip)
        """
        mdns_list = []
        if(len(current_services) > 0):
            for key, value in current_services.items():
                address = value['address']
                board = value['board'].capitalize()
                auth = value['auth_upload']

                caption = "{0} ({1})".format(board, address)
                mdns_list.append([caption, address, auth])

        return mdns_list