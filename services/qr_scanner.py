from evdev import InputDevice, list_devices, ecodes


class QRScanner:
    """
    Reads QR codes from the BF SCAN USB HID scanner.

    The scanner behaves like a keyboard, but we read its events
    directly through evdev so the scanned QR is not typed into
    the currently focused terminal/application.
    """

    VENDOR_ID = 0x9901
    PRODUCT_ID = 0x0301
    DEVICE_NAME = "BF SCAN SCAN KEYBOARD"

    def __init__(self):
        self.device = self._find_scanner()
        self._buffer = ""

        # Prevent scanner keystrokes from reaching the normal
        # keyboard/terminal input system.
        self.device.grab()

    def _find_scanner(self):
        for device_path in list_devices():
            try:
                device = InputDevice(device_path)

                if (
                    device.name == self.DEVICE_NAME
                    and device.info.vendor == self.VENDOR_ID
                    and device.info.product == self.PRODUCT_ID
                ):
                    return device

                device.close()

            except OSError:
                continue

        raise RuntimeError(
            "BF SCAN QR scanner not found. "
            "Check USB connection."
        )

    def read_scan(self):
        """
        Wait for and return one complete QR scan.

        The scanner sends the QR data as keyboard events,
        followed by Enter.
        """

        for event in self.device.read_loop():

            if event.type != ecodes.EV_KEY:
                continue

            # Only key-down events.
            if event.value != 1:
                continue

            key_name = ecodes.KEY.get(event.code)

            if not key_name:
                continue

            # End of scan
            if key_name in ("KEY_ENTER", "KEY_KPENTER"):
                qr_value = self._buffer
                self._buffer = ""

                if qr_value:
                    return qr_value

                continue

            character = self._key_to_character(key_name)

            if character:
                self._buffer += character

    @staticmethod
    def _key_to_character(key_name):
        mapping = {
            # Numbers
            "KEY_0": "0",
            "KEY_1": "1",
            "KEY_2": "2",
            "KEY_3": "3",
            "KEY_4": "4",
            "KEY_5": "5",
            "KEY_6": "6",
            "KEY_7": "7",
            "KEY_8": "8",
            "KEY_9": "9",

            # Letters
            "KEY_A": "A",
            "KEY_B": "B",
            "KEY_C": "C",
            "KEY_D": "D",
            "KEY_E": "E",
            "KEY_F": "F",
            "KEY_G": "G",
            "KEY_H": "H",
            "KEY_I": "I",
            "KEY_J": "J",
            "KEY_K": "K",
            "KEY_L": "L",
            "KEY_M": "M",
            "KEY_N": "N",
            "KEY_O": "O",
            "KEY_P": "P",
            "KEY_Q": "Q",
            "KEY_R": "R",
            "KEY_S": "S",
            "KEY_T": "T",
            "KEY_U": "U",
            "KEY_V": "V",
            "KEY_W": "W",
            "KEY_X": "X",
            "KEY_Y": "Y",
            "KEY_Z": "Z",

            # Common QR characters
            "KEY_MINUS": "-",
            "KEY_UNDERSCORE": "_",
            "KEY_DOT": ".",
            "KEY_SLASH": "/",
            "KEY_BACKSLASH": "\\",
            "KEY_EQUAL": "=",
            "KEY_PLUS": "+",
            "KEY_COLON": ":",
        }

        return mapping.get(key_name)

    @classmethod
    def check_health(cls):
        """
        Check whether the BF SCAN QR scanner is currently connected.

        Returns:
            (True, message) if scanner is found.
            (False, message) if scanner is not found.
        """

        for device_path in list_devices():
            try:
                device = InputDevice(device_path)

                if (
                    device.name == cls.DEVICE_NAME
                    and device.info.vendor == cls.VENDOR_ID
                    and device.info.product == cls.PRODUCT_ID
                ):
                    device.close()
                    return True, "BF SCAN QR scanner detected."

                device.close()

            except OSError:
                continue

        return False, "BF SCAN QR scanner not found."

    def close(self):
        """Release exclusive scanner access and close device."""

        if self.device:
            try:
                self.device.ungrab()
            except Exception:
                pass

            try:
                self.device.close()
            except Exception:
                pass

            self.device = None