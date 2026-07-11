-- ============================================================
-- Table : sync_state
-- Purpose : Local synchronization state
-- Platform : SQLite Only
-- ============================================================

CREATE TABLE sync_state
(
    sync_name      TEXT PRIMARY KEY,

    last_sync_ts   DATETIME,

    last_error_ts  DATETIME,

    last_error     TEXT
);
