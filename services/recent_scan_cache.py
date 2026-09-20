"""
recent_scan_cache.py

Maintains an in-memory cache of recently scanned QR codes.

Purpose
-------
Prevent duplicate processing while the same QR code
remains in front of the scanner.

Author  : Saravanakumar MJ
Project : QR Scanner
"""

from datetime import datetime, timedelta


class RecentScanCache:

    def __init__(self):

        self._cache = {}

    # --------------------------------------------------------
    # Load Cache
    # --------------------------------------------------------

    def load(self, records):
        """
        Loads the cache from recent scan records.
        """

        self.clear()

        for record in records:
            self._cache[
                record["qr_code"]
            ] = record["scan_ts"]

        return self.size()

    # --------------------------------------------------------
    # Exists
    # --------------------------------------------------------

    def exists(self, qr_code):

        return qr_code in self._cache

    # --------------------------------------------------------
    # Get Timestamp
    # --------------------------------------------------------

    def get_timestamp(self, qr_code):

        return self._cache.get(qr_code)

    # --------------------------------------------------------
    # Add
    # --------------------------------------------------------

    def add(self, qr_code, scan_ts):

        self._cache[qr_code] = scan_ts

        # --------------------------------------------------------
        # Cleanup
        # --------------------------------------------------------
            
    def cleanup(self, cache_cleanup_interval_secs):

        cutoff_time = (
            datetime.now().astimezone()
            - timedelta(
                seconds=cache_cleanup_interval_secs
            )
        )

        expired = []

        for qr_code, scan_ts in self._cache.items():

            if isinstance(scan_ts, str):

                scan_ts = datetime.fromisoformat(
                    scan_ts.replace("Z", "+00:00")
                )

            if scan_ts.tzinfo is None:

                scan_ts = scan_ts.replace(
                    tzinfo=cutoff_time.tzinfo
                )

            if scan_ts < cutoff_time:

                expired.append(qr_code)

        for qr_code in expired:

            del self._cache[qr_code]

        return (
            len(expired),
            cutoff_time.isoformat(timespec="seconds")
        )
    # --------------------------------------------------------
    # Clear
    # --------------------------------------------------------

    def clear(self):

        self._cache.clear()

    # --------------------------------------------------------
    # Size
    # --------------------------------------------------------

    def size(self):

        return len(self._cache)

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    def display(self):

        print("\n------ Recent Scan Cache ------")

        for qr_code, scan_ts in self._cache.items():

            print(
                f"{qr_code}   {scan_ts}"
            )

        print(
            f"\nTotal : {self.size()} QR Codes\n"
        )


# --------------------------------------------------------
# Global Cache Instance
# --------------------------------------------------------

recent_scan_cache = RecentScanCache()