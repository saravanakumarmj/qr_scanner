-- ============================================================
-- Table : qr_transaction
-- Purpose: Append-only QR scan transaction log
-- Platform: SQLite (Raspberry Pi)
-- ============================================================

CREATE TABLE qr_transaction
(
    transaction_id     TEXT PRIMARY KEY,

    qr_code            TEXT NOT NULL,

    device_id          TEXT NOT NULL,

    scan_ts            DATETIME NOT NULL,

    cycle_count        INTEGER NOT NULL
                            CHECK(cycle_count >= 0),

    scan_result        TEXT NOT NULL
                            CHECK(scan_result IN
                            (
                                'SUCCESS',
                                'FLAGGED',
                                'DISCARDED',
                                'INVALID',
                                'ERROR'
                            )),

    event_reason       TEXT
                            CHECK(event_reason IN
                            (
                                'CYCLE_LIMIT',
                                'AGE_LIMIT',
                                'DAMAGED'
                            )),

    result_code        TEXT NOT NULL,

    synced             INTEGER NOT NULL DEFAULT 0
                            CHECK(synced IN (0,1)),

    FOREIGN KEY (qr_code)
        REFERENCES qr_master(qr_code));
		
		
Recommended Indexes
CREATE INDEX idx_qr_transaction_qrcode
ON qr_transaction(qr_code);

CREATE INDEX idx_qr_transaction_device
ON qr_transaction(device_id);

CREATE INDEX idx_qr_transaction_scan_ts
ON qr_transaction(scan_ts);

CREATE INDEX idx_qr_transaction_result
ON qr_transaction(scan_result);

CREATE INDEX idx_qr_transaction_reason
ON qr_transaction(event_reason);

CREATE INDEX idx_qr_transaction_result_code
ON qr_transaction(result_code);

CREATE INDEX idx_qr_transaction_sync
ON qr_transaction(synced);
