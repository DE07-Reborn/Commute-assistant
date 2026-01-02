import time
from route_kafka.producers.route_request_producer import RouteRequestProducer
from route_kafka.utils.database_utils import Database_utils
from datetime import datetime
import logging
from zoneinfo import ZoneInfo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("route-scheduler")

producer = RouteRequestProducer()
db = Database_utils()

TIME_INTERVAL = 300 # second
LOOKAHEAD_MIN =  90 # minutes

KST = ZoneInfo("Asia/Seoul")

while True:
    now = datetime.now(KST).replace(tzinfo=None)

    logger.info("[IDLE] scheduler tick start")

    try:
        users = db.get_commute_candidates(
            now=now,
            lookahead_min=LOOKAHEAD_MIN
        )

        if not users:
            logger.info("[IDLE] no users in time window")
        
        logger.info(f'[DB] fetched {len(users)} users')

        for u in users:
            request_id = producer.send_topic(
                user_id=str(u["user_id"]),
                request_info={
                    "home_address": (u["home_lon"], u["home_lat"]),
                    "work_address": (u["work_lon"], u["work_lat"]),
                    "arrival_time": u["arrive_by"],
                    "feedback_time": u["feedback_min"],
                }
            )

            logger.info(
                "[SEND] route_request",
                extra={
                    "user_id": u["user_id"],
                    "request_id": request_id,
                    "arrive_by": u["arrive_by"].isoformat(),
                }
            )

        logger.info(
            "[SLEEP] scheduler sleeping",
            extra={"interval_sec": TIME_INTERVAL}
        )

    except Exception:
        logger.exception("[ERROR] scheduler loop failed")

    time.sleep(TIME_INTERVAL)