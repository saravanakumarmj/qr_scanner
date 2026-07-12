# FS-001 – Application Startup

## Version

1.0

---

# Purpose

This document defines the application startup sequence.

The startup process ensures that all mandatory services are operational before the scanner begins accepting QR scans.

If any mandatory validation fails, the application shall terminate.

---

# Startup Flow

```
Start Application
        ¦
        ?
Database Validation
        ¦
        ?
Internet Validation
        ¦
        ?
Supabase Connectivity
        ¦
        ?
Device Validation
        ¦
        ?
Configuration Download
        ¦
        ?
Application Ready
```

---

# Startup Sequence

| Step | Description | Mandatory |
|------|-------------|-----------|
|1|Database Validation|Yes|
|2|Internet Connectivity|Yes|
|3|Supabase Connectivity|Yes|
|4|Device Validation|Yes|
|5|Configuration Download|Yes|

---

# Pending Startup Modules

These modules are part of future releases.

| Module | Status |
|---------|--------|
|Scanner Validation|Pending|
|Relay Validation|Pending|
|Startup Synchronization|Pending|
|Subscription Validation|Pending|

---

# Startup Failure

If any mandatory startup validation fails

Application Status

FAILED

No scanner processing shall begin.

---

# Configuration Used

Downloaded from

app_configuration

---

# Output

Application enters READY state.

---

# Future Enhancements

• Scanner Validation

• Relay Validation

• Heartbeat

• Offline Configuration Cache

• Automatic Recovery

---

# Design Decision: Synchronization Interval and Recent Scan Cache

## Objective

The Raspberry Pi maintains a local SQLite database for high-speed scan processing while Supabase serves as the system of record. To ensure the local data remains current, the Raspberry Pi performs periodic synchronization with Supabase.

## Synchronization Interval

The synchronization interval is configured in the `app_configuration` table using the following parameter:

| Parameter               | Description                                                     |
| ----------------------- | --------------------------------------------------------------- |
| `sync_interval_minutes` | Frequency at which the Raspberry Pi synchronizes with Supabase. |

During every synchronization cycle, the Raspberry Pi performs the following operations:

1. Upload locally captured transactions to Supabase.
2. Download the latest `qr_master` data.
3. Download the latest application configuration.
4. Rebuild the `RecentScanCache`.

## RecentScanCache

`RecentScanCache` is an in-memory dictionary used to prevent the QR scanner from repeatedly processing the same QR code.

The cache is rebuilt during every synchronization cycle by downloading recent transactions from Supabase.

Only transactions belonging to the current `device_id` are loaded.

The time window used for loading recent transactions is equal to the configured `sync_interval_minutes`.

Example:

* `sync_interval_minutes = 1440`

During startup or synchronization, the Raspberry Pi downloads only transactions that satisfy:

* `device_id = Current Device`
* `scan_ts >= Current Time - 1440 minutes`

These records are loaded into `RecentScanCache`.

## Duplicate Scan Validation

Duplicate scan validation is performed entirely against `RecentScanCache`.

This avoids unnecessary database lookups for every scan while preventing repeated processing when the scanner reads the same QR code multiple times.

## Cache Cleanup

`RecentScanCache` is cleaned periodically based on the configured `cache_cleanup_minutes`.

Cleanup removes entries older than the current synchronization window.

Example:

* `sync_interval_minutes = 1440`
* `cache_cleanup_minutes = 120`

Every 120 minutes, cache entries older than 1440 minutes are removed.

## Design Rationale

This design provides the following benefits:

* Supabase remains the single source of truth.
* Raspberry Pi processes scans without querying the database for duplicate detection.
* Startup time remains fast because only recent transactions for the current device are downloaded.
* Memory usage remains predictable and bounded.
* All Raspberry Pi devices remain synchronized with the latest master data while operating independently.



End of Document