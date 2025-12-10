from kafka import KafkaAdminClient

BOOTSTRAP_SERVERS = "localhost:9092"


def main():
    print(f"Connecting to Kafka at {BOOTSTRAP_SERVERS}...")
    admin = KafkaAdminClient(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        client_id="healthcheck",
    )
    topics = admin.list_topics()
    print("Connected successfully.")
    print("Topics in cluster:")
    for t in topics:
        print(" -", t)
    admin.close()


if __name__ == "__main__":
    main()
