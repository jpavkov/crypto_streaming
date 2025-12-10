from datetime import datetime
from src.config.config import KAFKA_BOOTSTRAP_SERVERS, CRYPTO_SYMBOLS


def main():
    print("Binance producer stub")
    print(f"KAFKA_BOOTSTRAP_SERVERS={KAFKA_BOOTSTRAP_SERVERS}")
    print(f"CRYPTO_SYMBOLS={CRYPTO_SYMBOLS}")
    print(f"Started at {datetime.now()}")


if __name__ == "__main__":
    main()
