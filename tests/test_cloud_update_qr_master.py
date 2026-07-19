from cloud.repository import cloud_update_qr_master
#from database.repository import local_get_qr_master
from database.repository import local_lookup_qr

print()

print("Testing cloud_update_qr_master() 250217S0002 ")
print("--------------------------------")


#success, qr_master = local_get_qr_master("250217S0002")
success, qr_master, message = local_lookup_qr("250217S0002")

if not success:

    print(message)

else:
    print('lookup successful')

    success, message = cloud_update_qr_master([qr_master])

    print(success)

    print(message)


print("--------------------------------")