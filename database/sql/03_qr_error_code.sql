-- ============================================================
-- Table : qr_error_code
-- Purpose: Master list of application result/error codes
-- Platform: SQLite (Raspberry Pi)
-- ============================================================

CREATE TABLE qr_error_code
(
    result_code        TEXT PRIMARY KEY,

    result_type        TEXT NOT NULL
                            CHECK(result_type IN
                            (
                                'SUCCESS',
                                'FLAGGED',
                                'DISCARDED',
                                'INVALID',
                                'ERROR'
                            )),

    description        TEXT NOT NULL,

    active_status      INTEGER NOT NULL DEFAULT 1
                            CHECK(active_status IN (0,1))
);
