import pprint
import requests
import configparser
from inverter import Inverter
import const as c
import paho.mqtt.client as mqtt
import json
import os
import time
import logging

logging.basicConfig()
logging.root.setLevel(logging.WARN)
log=logging.getLogger(__name__)
log.setLevel(logging.INFO)


cfg = configparser.ConfigParser()
cfg.read(os.path.dirname(__file__) + '/config.ini')
_serial = cfg.getint('solarman','sn')
_host = cfg.get('solarman','host')
_port = cfg.getint('solarman','port',vars={'port':c.DEFAULT_PORT_INVERTER})
_mb_slave = cfg.getint('solarman','mb_slave',vars={'mb_slave': c.DEFAULT_INVERTER_MB_SLAVEID})
_inverter_file = "/{0}.yaml".format(cfg.get('default','inverter_type'))

log.info('Initializing inverter')

inv = Inverter(os.path.dirname(__file__) + '/inverter_definitions', _serial, _host, _port, _mb_slave, _inverter_file)
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(cfg.get('mqtt', 'username'), cfg.get('mqtt', 'password'))


handlers = []
def handle_webhook(data, last = None):
    _url = cfg.get('webhook', 'url')
    requests.post(_url, json=data)

def handle_sysout(data, last = None):
    pprint.pprint(data)

def handle_mqtt(curr, last = None):
    if (cfg.getboolean('mqtt', 'expand')):
        for k in curr.keys():
            _value = curr.get(k)
            if _value == last.get(k):
                continue
            if hasattr(_value, '__len__'):
                _value = json.dumps(_value)
            client.publish(cfg.get('mqtt', 'topic_prefix')+ '/'+k, _value, 1, True)
    else:
        client.publish(cfg.get('mqtt', 'topic_prefix'), json.dumps(curr), 1)

if (cfg.getboolean('default','print_to_sysout')):
    log.info('Sysout sensor publish is enabled')
    handlers.append(handle_sysout)

if (cfg.getboolean('webhook', 'enabled')):
    log.info('Webhook sensor publish is enabled')
    handlers.append(handle_webhook)

if (cfg.getboolean('mqtt', 'enabled')):
    log.info('Mqtt sensor publish is enabled')
    client.connect(cfg.get('mqtt', 'host'))
    client.loop_start()
    handlers.append(handle_mqtt)



_lastValue = None

while True:
    log.info('Pooling sensor values')
    inv.update()
    _curVal = inv.get_current_val()
    if _lastValue == None:
        _lastValue = _curVal
    
    for h in handlers:
        h(_curVal, _lastValue)

    _lastValue = _curVal
    time.sleep(15)
