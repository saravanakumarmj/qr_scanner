from cloud.repository import cloud_connect

print("\nTesting Cloud Connection...\n")

try:

    supabase = cloud_connect()

    print("PASS - Connected to Supabase")

except Exception as ex:

    print("FAIL")

    print(ex)