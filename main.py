import pprint
import requests
import configparser
from inverter import Inverter
import const as c
import paho.mqtt.client as mqtt
import json
import os

cfg = configparser.ConfigParser()
cfg.read('config.ini')
_serial = cfg.getint('solarman','sn')
_host = cfg.get('solarman','host')
_port = cfg.getint('solarman','port',vars={'port':c.DEFAULT_PORT_INVERTER})
_mb_slave = cfg.getint('solarman','mb_slave',vars={'mb_slave': c.DEFAULT_INVERTER_MB_SLAVEID})
_inverter_file = "/{0}.yaml".format(cfg.get('default','inverter_type'))

inv = Inverter(os.path.dirname(__file__) + '/inverter_definitions', _serial, _host, _port, _mb_slave, _inverter_file)

inv.update()
_curVal = inv.get_current_val()

if (cfg.getboolean('default','print_to_sysout')):
    pprint.pprint(_curVal)

if (cfg.getboolean('webhook', 'enabled')):
    _url = cfg.get('webhook', 'url')
    requests.post(_url, json=_curVal)

if (cfg.getboolean('mqtt', 'enabled')):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(cfg.get('mqtt', 'username'), cfg.get('mqtt', 'password'))
    client.connect(cfg.get('mqtt', 'host'))
    client.loop_start()
    
    if (cfg.getboolean('mqtt', 'expand')):
        for k in _curVal.keys():
            _value = _curVal.get(k)
            if hasattr(_value, '__len__'):
                _value = json.dumps(_value)
            client.publish(cfg.get('mqtt', 'topic_prefix')+ '/'+k, _value, 1)
    else:
        client.publish(cfg.get('mqtt', 'topic_prefix'), json.dumps(_curVal), 1)
    client.loop_stop()