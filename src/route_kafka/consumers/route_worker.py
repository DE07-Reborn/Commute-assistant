import os
from route_kafka.consumers.route_request_consumer import RouteKafkaConsumer
from route_kafka.utils.redis_route import RedisRoute
from route_kafka.utils.route_service import RouteService
from route_kafka.utils.google_api_utils import GoogleAPIUtils
import redis

def main():

    redis_client = redis.Redis(
        host = os.getenv("REDIS_HOST"),
        port = int(os.getenv("REDIS_PORT")),
        decode_responses=True,
    )
    redis_repo = RedisRoute(redis_client)
    google_api = GoogleAPIUtils()
    route_service = RouteService(google_api)

    consumer = RouteKafkaConsumer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP"),
        redis_repo=redis_repo,
        route_service=route_service,
    )
    consumer.start()

if __name__ == "__main__":
    main()