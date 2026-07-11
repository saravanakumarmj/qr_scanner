-- ============================================================
-- Table : qr_master
-- Purpose: Master record for every QR code ever generated
-- Platform: SQLite (Raspberry Pi)
-- ============================================================

CREATE TABLE qr_master
(
    qr_code             TEXT PRIMARY KEY,

    cycle_count         INTEGER NOT NULL DEFAULT 0
                            CHECK(cycle_count >= 0),

    qr_printed_ts       DATETIME NOT NULL,

    flagged             INTEGER NOT NULL DEFAULT 0
                            CHECK(flagged IN (0,1)),

    flag_reason         TEXT
                            CHECK(flag_reason IN
                            ('CYCLE_LIMIT',
                             'AGE_LIMIT',
                             'DAMAGED')),

    flag_mode           TEXT
                            CHECK(flag_mode IN
                            ('AUTO',
                             'MANUAL')),

    flag_device_id      TEXT,

    flagged_ts          DATETIME,

    active_status       INTEGER NOT NULL DEFAULT 1
                            CHECK(active_status IN (0,1)),

    discard_user        TEXT,

    discard_device_id   TEXT,

    discard_reason      TEXT
                            CHECK(discard_reason IN
                            ('CYCLE_LIMIT',
                             'AGE_LIMIT',
                             'DAMAGED')),

    discard_ts          DATETIME,

    created_ts          DATETIME NOT NULL
                            DEFAULT CURRENT_TIMESTAMP,

    updated_ts          DATETIME NOT NULL
                            DEFAULT CURRENT_TIMESTAMP,

    updated_by          TEXT NOT NULL,

    synced              INTEGER NOT NULL DEFAULT 0
                            CHECK(synced IN (0,1))
);

CREATE INDEX idx_qr_master_active
ON qr_master(active_status);

CREATE INDEX idx_qr_master_flagged
ON qr_master(flagged);

CREATE INDEX idx_qr_master_cycle
ON qr_master(cycle_count);

CREATE INDEX idx_qr_master_updated
ON qr_master(updated_ts);

CREATE INDEX idx_qr_master_sync
ON qr_master(synced);

CREATE INDEX idx_qr_master_printed
ON qr_master(qr_printed_ts);

CREATE INDEX idx_qr_master_flagged_ts
ON qr_master(flagged_ts);
