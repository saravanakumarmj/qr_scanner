"""
device_service.py

Handles device validation against the central server.

Current Version:
- Mock implementation
- Supabase integration will be added later.
"""

from dataclasses import dataclass

from config import DEVICE_ID


@dataclass
class DeviceValidationResult:
    success: bool
    message: str
    device_id: str
    customer_name: str = ""
    plant_name: str = ""
    line_name: str = ""
    max_cycle: int = 0
    subscription_valid: bool = False


class DeviceService:

    def __init__(self):
        pass

    def validate(self) -> DeviceValidationResult:

        print(f"Device ID : {DEVICE_ID}")

        #
        # TODO
        # Replace this section with actual Supabase validation.
        #

        return DeviceValidationResult(
            success=True,
            message="Device validation successful.",
            device_id=DEVICE_ID,
            customer_name="Demo Customer",
            plant_name="Demo Plant",
            line_name="Line-01",
            max_cycle=30,
            subscription_valid=True
        )
