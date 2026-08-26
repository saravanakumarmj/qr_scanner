"""Base36 encoding and decoding utilities."""

from __future__ import annotations


_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def encode_base36(value: int) -> str:
    """Convert a non-negative integer to uppercase Base36."""

    if value < 0:
        raise ValueError("Base36 value cannot be negative.")

    if value == 0:
        return "0"

    result = ""

    while value:
        value, remainder = divmod(value, 36)
        result = _ALPHABET[remainder] + result

    return result


def decode_base36(value: str) -> str:
    """Decode a Base36 value to its numeric string.

    If the value is not valid Base36, return the original value unchanged.
    """

    value = value.strip()

    if not value:
        return value

    try:
        result = 0

        for character in value.upper():
            if character not in _ALPHABET:
                return value

            result = result * 36 + _ALPHABET.index(character)

        return str(result)

    except (TypeError, ValueError):
        return value