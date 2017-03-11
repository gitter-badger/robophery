
import logging
import platform
import time
from importlib import import_module
from robophery.utils.rpi import detect_pi_version, detect_pi_revision

class ModuleManager(object):

    SERVICE_NAME = 'robophery-default'
    READ_INTERVAL = 10000
    PUBLISH_INTERVAL = 60000

    LINUX_PLATFORM = 'linux'
    RASPBERRYPI_PLATFORM = 'raspberrypi'
    BEAGLEBONE_PLATFORM = 'beaglebone'
    MINNOWBOARD_PLATFORM = 'minnowboard'
    NODEMCU_PLATFORM = 'nodemcu'
    FT232H_PLATFORM = 'ft232h'

    _instance = None

    _interface = {}
    _module = {}

    def __init__(self, *args, **kwargs):
        self._name = kwargs.get('name', self.SERVICE_NAME)
        self._platform = kwargs.get('platform', None)
        if self._platform == None:
            self._platform = self._detect_platform()
        self._read_interval = kwargs.get('read_interval', self.READ_INTERVAL)
        self._publish_interval = kwargs.get('publish_interval', self.PUBLISH_INTERVAL)
        self._log_level = kwargs.get('log_level', 'info')
        self._log_handlers = kwargs.get('log_level', ['console'])
        self._config = kwargs.get('config')
        self._run_mode = 'single' # multi
        self._setup_interfaces(self._config['interface'])
        self._setup_modules(self._config['module'])


    def _setup_log(self):
        self._log = logging.getLogger(self._name)
        if console in self._log_handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.ERROR)
            self._log.addHandler(console_handler)


    def _linux_platforms(self):
        return (
            self.RASPBERRYPI_PLATFORM,
            self.BEAGLEBONE_PLATFORM,
            self.MINNOWBOARD_PLATFORM
        )


    def _detect_platform(self):
        """
        Detect if device is running on the Raspberry Pi, Beaglebone
        Black or MinnowBoard and return the platform type.
        """

        # Detect Raspberry Pi
        pi = detect_pi_version()
        if pi is not None:
            return self.RASPBERRYPI_PLATFORM

        # Detect Beaglebone Black
        plat = platform.platform()
        if plat.lower().find('armv7l-with-debian') > -1:
            return self.BEAGLEBONE_PLATFORM
        elif plat.lower().find('armv7l-with-ubuntu') > -1:
            return self.BEAGLEBONE_PLATFORM
        elif plat.lower().find('armv7l-with-glibc2.4') > -1:
            return self.BEAGLEBONE_PLATFORM

        # Detect Minnowboard
        try:
            import mraa
            if mraa.getPlatformName()=='MinnowBoard MAX':
                return self.MINNOWBOARD_PLATFORM
        except ImportError:
            pass

        # Detect NodeMCU
        try:
            import pyb
            return self.NODEMCU_PLATFORM
        except ImportError:
            pass

        # Could not detect the platform, returning generic linux.
        return self.LINUX_PLATFORM


    def _setup_interfaces(self, interfaces={}):
        for interface_name, interface in interfaces.items():
            InterfaceClass = self._load_class(interface.pop('class'))
            if InterfaceClass:
                self._interface[interface_name] = InterfaceClass(**interface)


    def _setup_modules(self, modules={}):
        for module_name, module in modules.item():
            ModuleClass = self._load_class(module.pop('class'))
            module['interface'] = self._interface[module['interface']]
            module['manager'] = self
            if ModuleClass:
                self._module[module_name] = ModuleClass(**module)

    def _load_class(self, name):
        """
        Load class by path string
        """
        if isinstance(name, str):
            module = import_module(".".join(name.split(".")[:-1]))
            if module:
                return getattr(module, name.split(".")[-1], None)
            raise Exception("Cannot load class %s" % name)


    def _single_loop(self):
        """
        Run single global service loop
        """
        while True:
            data = self.get_data
            self._cache.append(data)
            print("Iteration: %s, read: %s" % (self._cycle_iteration, data))
            if self._cycle_iteration < self._cycle_size:
                self._cycle_iteration += 1
            else:
                self.publish_data(self._cache)
                print("Publishing: %s" % self._cache)
                self._cache = []
                self._cycle_iteration = 1
            time.sleep(self._read_interval / 1000)


    def run(self, modules=None):
        """
        Run robophery manager service
        """
        if self._run_mode == 'single':

            self._single_loop()

        else:

            for module in modules or self._module:
                if not module.own_loop:
                    self.loop.create_task(self.handle_module(module))
                else:
                    module.start_loop()

            try:
                self.loop.run_forever()
            except KeyboardInterrupt:
                for module in modules or self._module:
                    if module.own_loop:
                        module.stop_loop()
                self.loop.create_task(self.async_stop())
                self.loop.run_forever()
            finally:
                self.loop.close()



class Module(object):

    DEVICE_NAME = 'unknown-device'
    READ_INTERVAL = 10000
    PUBLISH_INTERVAL = 60000

    def __init__(self, *args, **kwargs):
        self._name = kwargs.get('name', self.DEVICE_NAME)
        self._manager = kwargs.get('manager', None)
        self._read_interval = kwargs.get('read_interval', self.READ_INTERVAL)


    def publish_data(self, data):
        print(data)


    @property
    def start_service(self):

        if self._publish_interval % self._read_interval != 0:
            raise RuntimeError('publish_interval must be divisible by read_interval.')
        self._cycle_size = self._publish_interval / self._read_interval
        self._cycle_iteration = 1
        self._cache = []
        print('Cycle size: %s' % self._cycle_size)
        self._service_loop()



class I2cModule(Module):

    def __init__(self, *args, **kwargs):
        self._bus = int(kwargs.get('busnum', '0'))
        super(I2cModule, self).__init__(*args, **kwargs)
        self._setup_device


    @property
    def _setup_device(self):
        if self._platform == self.RASPBERRYPI_PLATFORM:
            self._interface = SMBusInterface(self._addr, self._bus)
        elif self._platform == self.BEAGLEBONE_PLATFORM:
            self._interface = SMBusInterface(self._addr, self._bus)
        elif self._platform == self.FT232H_PLATFORM:
            self._interface = FT232Interface(self._addr)
        elif self._platform == self.NODEMCU_PLATFORM:
            self._interface = NodeMcuInterface(self._addr)
        else:
            raise RuntimeError('Platform not supported for I2C interface.')

        self.writeRaw8 = self._interface.writeRaw8
        self.write8 = self._interface.write8
        self.write16 = self._interface.write16
        self.writeList = self._interface.writeList
        self.readRaw8 = self._interface.readRaw8
        self.readU8 = self._interface.readU8
        self.readS8 = self._interface.readS8
        self.readU16 = self._interface.readU16
        self.readS16 = self._interface.readS16
        self.readList = self._interface.readList