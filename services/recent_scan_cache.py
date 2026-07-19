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

    def __init__(self, sync_interval_minutes=1440):

        self._cache = {}
        self._sync_interval_minutes = sync_interval_minutes

    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    def set_sync_interval(self, sync_interval_minutes):
        """
        Updates the synchronization interval.
        """

        self._sync_interval_minutes = sync_interval_minutes

    # --------------------------------------------------------
    # Load Cache
    # --------------------------------------------------------

    def load(self, records):
        """
        Loads the cache from recent transactions.

        records example:

        [
            {
                "qr_code": "260711S00001",
                "scan_ts": datetime(...)
            },
            ...
        ]
        """

        self.clear()

        for record in records:
            self._cache[record["qr_code"]] = record["scan_ts"]

        return self.size()

    # --------------------------------------------------------
    # Exists
    # --------------------------------------------------------

    def exists(self, qr_code):
        """
        Returns True if QR already exists in cache.
        """

        return qr_code in self._cache

    # --------------------------------------------------------
    # Add
    # --------------------------------------------------------

    def add(self, qr_code, scan_ts):
        """
        Adds a successfully processed QR into cache.
        """

        self._cache[qr_code] = scan_ts

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    def cleanup(self):
        """
        Removes expired QR codes from cache.

        Returns
        -------
        Number of entries removed.
        """

        cutoff_time = datetime.utcnow() - timedelta(
            minutes=self._sync_interval_minutes
        )

        expired = []

        for qr_code, scan_ts in self._cache.items():

            if scan_ts < cutoff_time:
                expired.append(qr_code)

        for qr_code in expired:
            del self._cache[qr_code]

        return len(expired)

    # --------------------------------------------------------
    # Clear
    # --------------------------------------------------------

    def clear(self):
        """
        Clears the entire cache.
        """

        self._cache.clear()

    # --------------------------------------------------------
    # Size
    # --------------------------------------------------------

    def size(self):
        """
        Returns number of QR codes currently in cache.
        """

        return len(self._cache)

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    def display(self):
        """
        Displays cache contents.
        Used only for debugging.
        """

        print("\n------ Recent Scan Cache ------")

        for qr_code, scan_ts in self._cache.items():
            print(f"{qr_code}   {scan_ts}")

        print(f"\nTotal : {self.size()} QR Codes\n")


# --------------------------------------------------------
# Global Cache Instance
# --------------------------------------------------------

recent_scan_cache = RecentScanCache()

