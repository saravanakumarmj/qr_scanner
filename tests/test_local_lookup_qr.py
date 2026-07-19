from database.repository import local_lookup_qr

QR_CODE = "250217S0002"

success, qr, message = local_lookup_qr(QR_CODE)

print()

print(f"Success : {success}")

if success:

    print("---------------------------")

    for key, value in qr.items():
        print(f"{key:<20}: {value}")

else:

    print(message)