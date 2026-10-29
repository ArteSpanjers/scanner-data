CREATE TABLE measurements (
    measurement_id UUID PRIMARY KEY,
    sha256 TEXT NOT NULL,
    object_key TEXT NOT NULL,
    state TEXT NOT NULL
        CHECK (state IN ('UPLOADING', 'COMPLETE', 'FAILED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);