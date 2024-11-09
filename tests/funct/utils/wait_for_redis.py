import time
import logging

from redis import Redis, ConnectionError

from tests.funct.settings import test_settings


def wait_for_redis(timeout=90, interval=5):
    es_client = Redis(
        host=test_settings.redis_settings.host,
        port=test_settings.redis_settings.port,
        password=test_settings.redis_settings.password,
    )
    start = time.time()

    while time.time() - start <= timeout:
        try:
            if es_client.ping():
                logging.info("Redis доступен.")
                break
            else:
                logging.warning("Ожидание Redis...")
        except ConnectionError:
            logging.error("Redis недоступен. Пробуем снова...")

        time.sleep(interval)


if __name__ == "__main__":
    wait_for_redis()
