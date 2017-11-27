VERSION = (2, 2, 0, '-dev.12')
__version__ = ".".join([str(s) for s in VERSION[:3]])
if(len(VERSION) > 3):
    __version__ += VERSION[3]

__title__ = "Deviot"
__description__ = (
    "Plugin for IoT development based in the platformIO ecosystem."
    "More info about platformIO visit: . http://platformio.org"
)
__url__ = "https://github.com/gepd/Deviot"

__author__ = "GEPD"
__email__ = "guillermoepd@gmail.com"

__copyright__ = "Copyright 2017 GEPD"
