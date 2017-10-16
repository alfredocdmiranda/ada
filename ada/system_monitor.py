import platform

import psutil


class SystemMonitor(object):
    def __init__(self, ada):
        self._ada = ada
        self.sys_info = platform.uname()
        self.python = platform.python_version()

    @property
    def temperature(self):
        temp = psutil.sensors_temperatures()['coretemp'][0]

        return temp

    @property
    def disk_usage(self):
        disk = psutil.disk_usage(self._ada.config['root'])

        return disk.percent

    @property
    def ada_version(self):
        version = self._ada.version

        return version