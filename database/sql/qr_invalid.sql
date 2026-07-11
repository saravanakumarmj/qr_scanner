-- ============================================================
-- Table : qr_invalid
-- Purpose: Stores invalid QR scans
-- Platform: SQLite (Raspberry Pi)
-- ============================================================

CREATE TABLE qr_invalid
(
    invalid_id        INTEGER PRIMARY KEY AUTOINCREMENT,

    raw_code          TEXT NOT NULL,

    device_id         TEXT NOT NULL,

    scan_ts           DATETIME NOT NULL,

    result_code       TEXT NOT NULL,

    synced            INTEGER NOT NULL DEFAULT 0
                          CHECK(synced IN (0,1))
);

CREATE INDEX idx_qr_invalid_scan_ts
ON qr_invalid(scan_ts);

CREATE INDEX idx_qr_invalid_device
ON qr_invalid(device_id);

CREATE INDEX idx_qr_invalid_result
ON qr_invalid(result_code);

CREATE INDEX idx_qr_invalid_sync
ON qr_invalid(synced);
