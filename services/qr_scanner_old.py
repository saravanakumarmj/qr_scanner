"""
qr_scanner.py

USB HID QR scanner service.

The scanner behaves like a keyboard and sends the
scanned QR value followed by an Enter key.

This module is responsible only for reading the scanner.
It does not perform QR validation, database operations,
decoding, uploading, or business-rule processing.
"""

from evdev import InputDevice
from evdev import list_devices
from evdev import ecodes


class QRScanner:

    def __init__(self):
        """
        Find and open the QR scanner.
        """

        self.device = self._find_scanner()

        self._buffer = ""

    # ---------------------------------------------------------
    # Find Scanner
    # ---------------------------------------------------------

    def _find_scanner(self):
        """
        Automatically find the BF SCAN USB keyboard.

        Returns
        -------
        InputDevice

        Raises
        ------
        RuntimeError
            If the scanner cannot be found.
        """

        devices = list_devices()

        for device_path in devices:

            try:
                device = InputDevice(device_path)

                name = device.name.upper()

                if "BF SCAN" in name:

                    return device

                device.close()

            except OSError:
                continue

        raise RuntimeError(
            "QR scanner not found. "
            "Check that the BF SCAN scanner is connected."
        )

    # ---------------------------------------------------------
    # Read Scan
    # ---------------------------------------------------------

    def read_scan(self):
        """
        Wait for one complete QR scan.

        Returns
        -------
        str
            Raw QR value.
        """

        for event in self.device.read_loop():

            if event.type != ecodes.EV_KEY:
                continue

            if event.value != 1:
                continue

            key_name = ecodes.KEY.get(event.code)

            if not key_name:
                continue

            # ---------------------------------------------
            # Enter = end of scan
            # ---------------------------------------------

            if key_name in ("KEY_ENTER", "KEY_KPENTER"):

                qr_value = self._buffer

                self._buffer = ""

                if qr_value:
                    return qr_value

                continue

            # ---------------------------------------------
            # Normal keyboard character
            # ---------------------------------------------

            if key_name.startswith("KEY_"):

                character = self._key_to_character(
                    key_name
                )

                if character:
                    self._buffer += character

    # ---------------------------------------------------------
    # Convert Key
    # ---------------------------------------------------------

    @staticmethod
    def _key_to_character(key_name):
        """
        Convert an evdev key name into a character.

        Supports the characters normally used by our
        QR codes.
        """

        mapping = {

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

            "KEY_MINUS": "-",
            "KEY_UNDERSCORE": "_",

        }

        return mapping.get(key_name)

    # ---------------------------------------------------------
    # Close
    # ---------------------------------------------------------

    def close(self):
        """
        Close the scanner device.
        """

        if self.device:
            self.device.close()

    @classmethod
    def check_health(cls):
        """
        Check whether the BF SCAN USB scanner is available.

        This does not create the scanner reader.
        """

        try:
            device = cls().device

            device.close()

            return (
                True,
                "QR scanner is connected."
            )

        except RuntimeError as ex:

            return (
                False,
                str(ex)
            )

        except OSError as ex:

            return (
                False,
                f"QR scanner error: {ex}"
            )

        except Exception as ex:

            return (
                False,
                f"QR scanner health check failed: {ex}"
            )
