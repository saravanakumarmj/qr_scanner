import os

def get_zero_2w_id():
    try:
        with open('/sys/firmware/devicetree/base/serial-number', 'r') as f:
            return f.read().strip().replace('\x00', '')
    except FileNotFoundError:
        return "UNKNOWN_DEVICE"

print("Your Pi Zero 2 W Unique Code:", get_zero_2w_id())
