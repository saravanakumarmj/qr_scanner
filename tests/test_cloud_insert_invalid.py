from cloud.repository import cloud_insert_invalid_qr
from database.repository import local_get_pending_invalid

print()
print("Testing cloud_insert_invalid_qr()")
print("--------------------------------")

success, result = local_get_pending_invalid()

if not success:

    print(result)

elif len(result) == 0:

    print("No pending invalid QR records.")

else:

    success, message = cloud_insert_invalid_qr(result)

    print(f"Success : {success}")
    print(f"Message : {message}")

print("--------------------------------")