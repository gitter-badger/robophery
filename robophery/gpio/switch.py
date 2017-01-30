#!/usr/bin/python

import logging
from robophery.gpio import GpioModule

logger = logging.getLogger("robophery.gpio.switch")


class SwitchModule(GpioModule):


    def __init__(self, kwargs)
        self.name = kwargs.get('name')
        self.set_port(kwargs.get('port'))


    @property
    def get_data():
        """
        Switch status readings.
        """

        GPIO.setup(port, GPIO.IN)
        state = GPIO.input(self.port)

        press_count = press_delta = state
     
        values = [
            ('%s.press_count' % self.name, press_count, ),
            ('%s.press_delta' % self.name, press_delta, ),
        ]
        return values


    @property
    def get_meta_data():
        """
        Get the readings meta-data.
        """
        return {
            'press_count': {
                'type': 
                'unit': 'total seconds pressed',
                'range_low': 0,
                'range_high': None,
                'sensor': 'switch'
            },
            'press_delta': {
                'type': 
                'unit': 'seconds pressed per period',
                'range_low': 0,
                'range_high': None,
                'sensor': 'switch'
            }

        }
