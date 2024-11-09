import time
import logging

from elasticsearch import Elasticsearch, ConnectionError

from tests.funct.settings import test_settings


def wait_for_es(timeout=90, interval=5):
    es_client = Elasticsearch(hosts=[test_settings.es_settings.get_url()])
    start = time.time()

    while time.time() - start <= timeout:
        try:
            if es_client.ping():
                logging.info("Elasticsearch доступен.")
                break
            else:
                logging.warning("Ожидание Elasticsearch...")
        except ConnectionError:
            logging.error("Elasticsearch недоступен. Пробуем снова...")

        time.sleep(interval)


if __name__ == "__main__":
    wait_for_es()
