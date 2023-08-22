import redis
import requests
import time


def wait_for_weaviate():
    while True:
        try:
            response = requests.get("http://weaviate:8080/v1/.well-known/live")
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(5)


def wait_for_redis(host="redis", port=6379):
    while True:
        try:
            r = redis.Redis(host=host, port=port)
            r.ping()  # Sends a PING command to the Redis server
            break  # If the ping is successful, break out of the loop
        except redis.ConnectionError:
            time.sleep(
                5
            )  # If there's a connection error, wait for 5 seconds and try again
