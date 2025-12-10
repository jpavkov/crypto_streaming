import json
from typing import List, Tuple

from kafka import KafkaConsumer
import snowflake.connector

from src.config.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
    SNOWFLAKE_ACCOUNT,
    SNOWFLAKE_USER,
    SNOWFLAKE_PASSWORD,
    SNOWFLAKE_ROLE,
    SNOWFLAKE_WAREHOUSE,
    SNOWFLAKE_DATABASE,
    SNOWFLAKE_SCHEMA,
    SNOWFLAKE_TABLE,
)

BATCH_SIZE = 50  # number of messages per insert


def get_snowflake_connection():
    print("[SF] Creating Snowflake connection (password auth)...")
    if not all(
        [
            SNOWFLAKE_ACCOUNT,
            SNOWFLAKE_USER,
            SNOWFLAKE_PASSWORD,
            SNOWFLAKE_WAREHOUSE,
            SNOWFLAKE_DATABASE,
            SNOWFLAKE_SCHEMA,
        ]
    ):
        raise RuntimeError(
            "Snowflake config incomplete. Check .env for "
            "SNOWFLAKE_ACCOUNT, USER, PASSWORD, WAREHOUSE, DATABASE, SCHEMA."
        )

    conn_args = {
        "account": SNOWFLAKE_ACCOUNT,
        "user": SNOWFLAKE_USER,
        "password": SNOWFLAKE_PASSWORD,
        "warehouse": SNOWFLAKE_WAREHOUSE,
        "database": SNOWFLAKE_DATABASE,
        "schema": SNOWFLAKE_SCHEMA,
    }

    if SNOWFLAKE_ROLE:
        conn_args["role"] = SNOWFLAKE_ROLE

    conn = snowflake.connector.connect(**conn_args)
    print("[SF] Connected to Snowflake.")
    return conn


def write_batch_to_snowflake(
    conn,
    rows: List[Tuple[str, str, str, str, str]],
):
    """
    rows: list of tuples (source, endpoint, ticker, ts_ingested, payload_json_str)
    """
    if not rows:
        return

    sql = f"""
        INSERT INTO {SNOWFLAKE_TABLE} (SOURCE, ENDPOINT, TICKER, TS_INGESTED, PAYLOAD)
        VALUES (%s, %s, %s, %s, %s)
    """

    with conn.cursor() as cur:
        cur.executemany(sql, rows)

    print(f"[SF] Inserted {len(rows)} rows into {SNOWFLAKE_TABLE}")


def main():
    print("Starting Kafka → Snowflake consumer...")
    print(f"Bootstrap servers: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Topic: {KAFKA_TOPIC}")
    print(
        f"Snowflake target: {SNOWFLAKE_ACCOUNT}/{SNOWFLAKE_DATABASE}/{SNOWFLAKE_SCHEMA}.{SNOWFLAKE_TABLE}"
    )

    conn = get_snowflake_connection()

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="market-consumers-snowflake",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
    )

    batch: List[Tuple[str, str, str, str, str]] = []

    try:
        print("[KAFKA] Consumer started. Waiting for messages...")
        for message in consumer:
            key = message.key
            value = message.value

            source = value.get("source")
            endpoint = value.get("endpoint")
            ts_ingested = value.get("ts_ingested")
            payload = value.get("payload", {})
            ticker = payload.get("ticker") or key

            payload_json_str = json.dumps(payload)

            batch.append((source, endpoint, ticker,
                         ts_ingested, payload_json_str))

            print(f"[CONSUMED] key={key} | ticker={ticker}")

            if len(batch) >= BATCH_SIZE:
                write_batch_to_snowflake(conn, batch)
                batch.clear()

    except KeyboardInterrupt:
        print("Stopping consumer (Ctrl+C)...")
    finally:
        if batch:
            write_batch_to_snowflake(conn, batch)
            batch.clear()

        consumer.close()
        conn.close()
        print("Consumer and Snowflake connection closed.")


if __name__ == "__main__":
    main()
