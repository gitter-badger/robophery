#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from oslo_config import cfg
from robophery.base import ModuleManager
from robophery.conf import *

GPIO_OPTS = [
    cfg.Opt('data_pin',
        short='p',
        help='Module GPIO pin'),
]

BLE_OPTS = [
    cfg.Opt('addr',
        short='a',
        help='Module MAC address'),
]


def _config(module_conf, opts = None):
    conf = {
        'log_level': 'debug',
        'log_handlers': ['console',],
        'read_interval': 2000,
        'platform': 'raspberrypi',
        'config': RPI_PLATFORM
    }
    conf['config']['module'] = {
        'module': module_conf,
    }
    if opts != None:
        CONF = cfg.CONF
        CONF.register_cli_opts(opts)
        CONF(sys.argv[1:])
        conf['config']['module']['module'].update(CONF)
    return conf

# I2C modules


def module_bmp085():
    config = _config(BMP085_MODULE)
    manager = ModuleManager(**config)
    manager.run()


def module_bh1750():
    config = _config(BH1750_MODULE)
    manager = ModuleManager(**config)
    manager.run()


def module_htu21d():
    config = _config(HTU21D_MODULE)
    manager = ModuleManager(**config)
    manager.run()


def module_mcp9808():
    config = _config(MCP9808_MODULE)
    manager = ModuleManager(**config)
    manager.run()

# GPIO modules


def module_dht11():
    config = _config(DHT11_MODULE, GPIO_OPTS)
    manager = ModuleManager(**config)
    if config['config']['module']['module']['data_pin'] == None:
        raise ValueError("Data pin must be set.")
    manager.run()


def module_dht22():
    config = _config(DHT22_MODULE, GPIO_OPTS)
    manager = ModuleManager(**config)
    if config['config']['module']['module']['data_pin'] == None:
        raise ValueError("Data pin must be set.")
    manager.run()


def module_l293d():
    OPTS = [
        cfg.Opt('power_pin',
            short='a',
            help='L293D pin 1 or pin 9: On or off'),
        cfg.Opt('forward_pin',
            short='b',
            help='L293D pin 2 or pin 10: Anticlockwise positive'),
        cfg.Opt('backward_pin',
            short='c',
            help='L293D pin 7 or pin 15: Clockwise positive'),
    ]
    config = _config(L293D_MODULE, OPTS)
    if config['config']['module']['module']['power_pin'] == None:
        raise ValueError("Power pin must be set.")
    if config['config']['module']['module']['forward_pin'] == None:
        raise ValueError("Forward pin must be set.")
    if config['config']['module']['module']['backward_pin'] == None:
        raise ValueError("Backward pin must be set.")
    manager = ModuleManager(**config)
    manager.run()


def module_relay():
    config = _config(RELAY_MODULE, GPIO_OPTS)
    manager = ModuleManager(**config)
    if config['config']['module']['module']['data_pin'] == None:
        raise ValueError("Data pin must be set.")
    manager.run()


def module_switch():
    config = _config(SWITCH_MODULE, GPIO_OPTS)
    manager = ModuleManager(**config)
    if config['config']['module']['module']['data_pin'] == None:
        raise ValueError("Data pin must be set.")
    manager.run()

# BLE modules


def module_pfp():
    config = _config(PFP_MODULE, BLE_OPTS)
    if config['config']['module']['module']['addr'] == None:
        raise ValueError("MAC address must be set.")
    manager = ModuleManager(**config)
    manager.run()

# 1-wire modules


def module_ds18():
    OPTS = [
        cfg.Opt('type',
            short='t',
            default="ds18b20",
            help='Specific type of Dallas DS18 family midule.'),
        cfg.Opt('addr',
            short='a',
            default='0',
            help='Specific module address at 1-wire bus.')
    ]
    config = _config(DS18_MODULE, OPTS)
    manager = ModuleManager(**config)
    manager.run()
