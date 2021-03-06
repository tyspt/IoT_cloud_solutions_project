import json
import requests
import logging
import RPi.GPIO as GPIO

import credential as cr

""" Module respobsible for controlling the offline devices connected to Raspberry Pi or Arduino with 
    either REST Http requests through LAN or messages through serial connection.
"""

# There are two way to control local devices in my project, using Http requests for the ones that are connected on my
# phillips hue bridge, or direct through raspberrry which are connected to a relay.
# Refer to the following page for more information about phillips hue bridge commands: https://developers.meethue.com/develop/get-started-2/

HUE_BRIDGE_HTTP_DEVICES = {"grow_light": "http://philips-hue/api/{}/lights/5/".format(cr.hue_bridge_api_key),
                           "air_pump": "http://philips-hue/api/{}/lights/3/".format(cr.hue_bridge_api_key)}
RELAY_DEVICES = {
    "water_pump_1": {
        "state_on": False,
        "GPIO_PIN": 17}}

def toggle_device(device_name, command):
    logging.info("(Device Control) device controlling info received, device: {} -> command: {}".format(device_name,
                                                                                                       command))
    is_turn_on = False
    if command.upper() == "ON":
        is_turn_on = True
    if device_name in HUE_BRIDGE_HTTP_DEVICES.keys():
        _toggle_device_through_http_request(device_name, is_turn_on)
    elif device_name in RELAY_DEVICES.keys():
        _toggle_device_with_gpio_relay(device_name,is_turn_on)
    else:
        logging.warning(
            "(Device Control) unable to control device {}, because it doesn't exist in global configs".format(device_name))

def get_status(device_name):
    if device_name in HUE_BRIDGE_HTTP_DEVICES.keys():
        return _get_hue_http_device_status(device_name)
    elif device_name in RELAY_DEVICES.keys():
        return _get_relay_device_status(device_name)

def _get_hue_http_device_status(device_name):
    endpoint = HUE_BRIDGE_HTTP_DEVICES[device_name]
    # sending get request and saving the response as response object
    r = requests.get(url=endpoint)
    # extracting data in json format
    response = r.json()
    # extracting data
    status = response["state"]["on"]
    if status is True:
        return "on"
    else:
        return "off"

def _get_relay_device_status(device_name):
    if RELAY_DEVICES[device_name]["state_on"]:
        return "on"
    else:
        return "off" 

def _toggle_device_through_http_request(device_name, is_turn_on):
    endpoint = HUE_BRIDGE_HTTP_DEVICES[device_name] + "state"
    
    data = json.dumps({"on": is_turn_on})

    # sending put request and saving response as response object
    r = requests.put(url=endpoint, data=data)

    # extracting response text
    pastebin_url = r.text

    logging.info("(Device Control) device {} is turned {}, message: {}".format(
        device_name, command, pastebin_url))


def _toggle_device_with_gpio_relay(device_name, is_turn_on):
    GPIO.setmode(GPIO.BCM)  # GPIO Numbers instead of board numbers
    gpio_pin = RELAY_DEVICES[device_name]["GPIO_PIN"]
    GPIO.setup(gpio_pin, GPIO.OUT)  # GPIO Assign mode
    if is_turn_on:
        GPIO.output(gpio_pin, GPIO.HIGH)  # on
        RELAY_DEVICES[device_name]["state_on"] = True
        logging.info("(Device Control) device {} is turned on".format(
            device_name))
    else:
        GPIO.output(gpio_pin, GPIO.LOW)  # out
        RELAY_DEVICES[device_name]["state_on"] = False
        logging.info("(Device Control) device {} is turned off".format(
            device_name))

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s",
                        level=logging.DEBUG)
    # toggle_device("grow_light", "off")
    toggle_device("water_pump_1", "on")
    print(get_relay_device_status("water_pump_1"))
