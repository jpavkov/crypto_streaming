from datetime import datetime
from src.config.config import KAFKA_BOOTSTRAP_SERVERS


def main():
    print("Snowflake consumer stub")
    print(f"KAFKA_BOOTSTRAP_SERVERS={KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Started at {datetime.now()}")


if __name__ == "__main__":
    main()
