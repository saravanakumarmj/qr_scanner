# FS-002 – QR Scan Processing

## Version

1.0

---

# Purpose

Defines the complete processing flow after a QR code is scanned.

This document represents the core business logic of the QR Scanner System.

---

# Processing Flow

```
Scanner
    ¦
    ?
Read QR
    ¦
    ?
Validation Engine
    ¦
    +-- QR Exists
    +-- Active Status
    +-- Duplicate Scan
    +-- Maximum Age
    +-- Maximum Cycle
    ¦
    ?
Decision
```

---

# Validation Order

The validation order shall never change.

|Order|Validation|
|-----|----------|
|1|QR Exists|
|2|QR Active|
|3|Duplicate Scan|
|4|Maximum Can Age|
|5|Maximum Cycle Count|

---

# Rule 1

## QR Exists

Verify the QR exists in local SQLite.

Failure Result

QR_NOT_FOUND

Actions

• Insert qr_invalid

• Insert qr_transaction

• Activate Relay

• RED LED

---

# Rule 2

## QR Active

Verify

active_status = ACTIVE

Failure Result

QR_INACTIVE

Actions

• Insert qr_invalid

• Insert qr_transaction

• RED LED

• Relay

---

# Rule 3

## Duplicate Scan

Configuration

duplicate_scan_minutes

Logic

If the same QR is scanned within the configured interval

Failure Result

DUPLICATE_SCAN

Actions

• Insert qr_transaction

• RED LED

• Relay

No master update.

---

# Rule 4

## Maximum Can Age

Configuration

max_can_age_days

Logic

Current DateTime

minus

qr_printed_ts

Failure Result

AGE_LIMIT

Actions

• Insert qr_transaction

• RED LED

• Relay

No master update.

---

# Rule 5

## Maximum Cycle Count

Configuration

max_cycle

Logic

If

current_cycle >= max_cycle

Failure Result

CYCLE_LIMIT

Actions

• Insert qr_transaction

• RED LED

• Relay

No master update.

---

# Successful Scan

When every validation succeeds

Processing Sequence

1. Insert qr_transaction

2. Increment cycle count

3. Update qr_master

4. GREEN LED

5. Continue scanning

---

# Validation Result Codes

SUCCESS

QR_NOT_FOUND

QR_INACTIVE

DUPLICATE_SCAN

AGE_LIMIT

CYCLE_LIMIT

DATABASE_ERROR

UNKNOWN_ERROR

---

# Configuration Used

max_cycle

duplicate_scan_minutes

max_can_age_days

relay_on_time

---

# Database Updates

## Success

Update

qr_master

Insert

qr_transaction

---

## Failure

Insert

qr_transaction

Insert

qr_invalid (where applicable)

No update to qr_master.

---

# Future Enhancements

• Multiple Validation Errors

• Manual Override

• Supervisor Approval

• Duplicate Scan Exceptions

• Age Exception Rules

• Factory-specific Rules

---

End of Document