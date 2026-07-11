CREATE TABLE qr_device
(
    device_id         TEXT PRIMARY KEY,
    device_name       TEXT NOT NULL,
    location          TEXT,
    app_version       TEXT,
    registered_ts     DATETIME NOT NULL,
    last_heartbeat_ts DATETIME
);
