import os

# In the future we'll read these from env vars or a config file.
KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
CRYPTO_SYMBOLS = os.getenv(
    "CRYPTO_SYMBOLS", "BTCUSDT,ETHUSDT,SOLUSDT").split(",")

# Snowflake settings (placeholders for now)
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT", "")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER", "")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD", "")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE", "")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "")
