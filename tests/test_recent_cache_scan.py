"""
test_recent_cache_scan.py

Unit test for RecentScanCache.

Author : Saravanakumar MJ
Project : QR Scanner
"""

from datetime import datetime

from services.recent_scan_cache import RecentScanCache


cache = RecentScanCache()

records = [
    {
        "qr_code": "TEST001",
        "scan_ts": datetime.now()
    }
]

count = cache.load(records)

print(f"Loaded : {count}")

print(cache.exists("TEST001"))

print(cache.exists("TEST999"))

cache.add(
    "TEST002",
    datetime.now()
)

print(cache.size())





removed = cache.cleanup()

print(f"Removed : {removed}")

print(f"Load Count        : {count}")
print(f"TEST001 Exists    : {cache.exists('TEST001')}")
print(f"TEST999 Exists    : {cache.exists('TEST999')}")
print(f"Cache Size        : {cache.size()}")
print(f"Removed Entries   : {removed}")



cache.display()


