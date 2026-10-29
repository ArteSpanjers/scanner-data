import psycopg
from psycopg.rows import DictRow, dict_row


def claim_measurement(measurement_id, checksum, object_key):
    with psycopg.connect(connect_timeout=5) as conn:
        row = conn.execute(
            """
            INSERT INTO measurements (
                measurement_id, sha256, object_key, state
            )
            VALUES (%s, %s, %s, 'UPLOADING')
            ON CONFLICT (measurement_id) DO NOTHING
            RETURNING measurement_id
            """,
            (measurement_id, checksum, object_key),
        ).fetchone()

    return row is not None

def set_measurement_state(measurement_id, state):
    with psycopg.connect(connect_timeout=5) as conn:
        conn.execute(
            """
            UPDATE measurements
            SET state = %s
            WHERE measurement_id = %s
            """,
            (state, measurement_id),
        )

def get_measurement(measurement_id):
    with psycopg.Connection[DictRow].connect(
        connect_timeout=5,
        row_factory=dict_row,
    ) as conn:
        return conn.execute(
            """
            SELECT measurement_id, sha256, object_key, state
            FROM measurements
            WHERE measurement_id = %s
            """,
            (measurement_id,),
        ).fetchone()

def reclaim_failed_measurement(measurement_id, checksum):
    with psycopg.connect(connect_timeout=5) as conn:
        row = conn.execute(
            """
            UPDATE measurements
            SET state = 'UPLOADING'
            WHERE measurement_id = %s
              AND sha256 = %s
              AND state = 'FAILED'
            RETURNING measurement_id
            """,
            (measurement_id, checksum),
        ).fetchone()

    return row is not None