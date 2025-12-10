import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

import requests
from kafka import KafkaProducer

from src.config.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
    MASSIVE_API_KEY,
    MASSIVE_BASE_URL,
)


def create_producer() -> KafkaProducer:
    """Create a Kafka producer with JSON value serialization."""
    print(f"Creating Kafka producer to {KAFKA_BOOTSTRAP_SERVERS}...")
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
    )
    return producer


def massive_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generic helper to call Massive REST API with Bearer auth.
    """
    if not MASSIVE_API_KEY:
        raise RuntimeError(
            "MASSIVE_API_KEY is not set. Make sure it exists in your .env file.")

    url = f"{MASSIVE_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {MASSIVE_API_KEY}",
    }

    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def fetch_dividends(ticker: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Example using the Dividends endpoint from Massive docs.
    You can swap this out later for trades/quotes.
    """
    params: Dict[str, Any] = {}
    if ticker:
        params["ticker"] = ticker

    data = massive_get("/v3/reference/dividends", params=params)
    # Massive format: { "results": [...], "status": "...", "request_id": "..." }
    results = data.get("results", [])
    return results


def main():
    print("Starting Massive → Kafka producer...")
    print(f"Kafka topic: {KAFKA_TOPIC}")
    print(f"Massive base URL: {MASSIVE_BASE_URL}")

    producer = create_producer()

    try:
        while True:
            try:
                results = fetch_dividends()
            except Exception as e:
                print(f"[ERROR] Failed to fetch Massive dividends: {e}")
                time.sleep(60)
                continue

            for record in results:
                msg = {
                    "source": "massive",
                    "endpoint": "reference/dividends",
                    "ts_ingested": datetime.now(timezone.utc).isoformat(),
                    "payload": record,  # raw Massive JSON record
                }

                key = record.get("ticker", "UNKNOWN")

                producer.send(KAFKA_TOPIC, key=key, value=msg)
                print(
                    f"[PRODUCED] key={key} | payload_ticker={record.get('ticker')}")

            producer.flush()
            time.sleep(60)

    except KeyboardInterrupt:
        print("Stopping Massive producer (Ctrl+C).")
    finally:
        producer.close()
        print("Producer closed.")


if __name__ == "__main__":
    main()
