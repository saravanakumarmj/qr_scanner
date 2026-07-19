CREATE TABLE public.qr_invalid
(
    invalid_id      UUID PRIMARY KEY,

    raw_code        TEXT NOT NULL,

    device_id       TEXT NOT NULL,

    scan_ts         TIMESTAMP NOT NULL,

    result_code     TEXT NOT NULL,

    CONSTRAINT qr_invalid_device_id_fkey
        FOREIGN KEY (device_id)
        REFERENCES qr_device(device_id),

    CONSTRAINT qr_invalid_result_code_fkey
        FOREIGN KEY (result_code)
        REFERENCES qr_error_code(result_code)
);

CREATE INDEX idx_qr_invalid_scan_ts
ON public.qr_invalid(scan_ts DESC);

CREATE INDEX idx_qr_invalid_device
ON public.qr_invalid(device_id);

CREATE INDEX idx_qr_invalid_result
ON public.qr_invalid(result_code);