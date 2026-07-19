from cloud.repository import lookup_qr

success, qr, message = lookup_qr(
    "YOUR_QR_CODE"
)

print()

print(f"Success : {success}")

if success:

    print(f"QR Code      : {qr['qr_code']}")
    print(f"Cycle Count  : {qr['cycle_count']}")
    print(f"Flagged      : {qr['flagged']}")
    print(f"Flag Reason  : {qr['flag_reason']}")

else:

    print(message)