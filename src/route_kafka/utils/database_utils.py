import psycopg2
import os
from datetime import datetime, timedelta

class Database_utils:
    """
        Connect to PostgresDB to inspect and get data
    """

    def __init__(self):
        self.conn = psycopg2.connect(
            host = os.getenv('APP_DB_HOST'),
            database = os.getenv('APP_DB_NAME'),
            user = os.getenv('APP_DB_USER'),
            password = os.getenv('APP_DB_PSWD')
        )
        self.conn.autocommit = True



    def get_commute_candidates(
        self,
        now: datetime,
        lookahead_min: int = 90,
    ):
        """
            Fetch users whose arrival deadline (commute_time - 10minute)
            is within [now + 35min(for alert), now + lookahead_min]
            Default lookahead minute is 90 which means 60minutes for all cases of 
            commuting time plus 30 minutes for extra time of alert time
        """
        startpoint = now + timedelta(minutes=35)
        endpoint = now + timedelta(minutes=lookahead_min)

        query = """
            SELECT
                u.id as user_id
                , ua.home_lat
                , ua.home_lon
                , ua.work_lat
                , ua.work_lon
                , (date_trunc('day', now()) + up.commute_time - INTERVAL '10 minutes') 
                    as arrive_by
                , COALESCE(up.feedback_min, 0) as feedback_min
            FROM users u
            JOIN user_profile up
                ON u.id = up.id
            JOIN user_address ua
                ON u.id = ua.id
            WHERE
                up.commute_time IS NOT NULL
                AND (date_trunc('day', now()) + up.commute_time - INTERVAL '10 minutes') 
                    BETWEEN %(startpoint)s AND %(endpoint)s
            ORDER BY arrive_by ASC
        """

        with self.conn.cursor() as cur:
            cur.execute(
                query,
                {
                    "startpoint" : startpoint,
                    "endpoint" : endpoint
                }
            )
            rows = cur.fetchall()
        
        return [
            {
                "user_id": r[0],
                "home_lat": float(r[1]),
                "home_lon": float(r[2]),
                "work_lat": float(r[3]),
                "work_lon": float(r[4]),
                "arrive_by": r[5],
                "feedback_min": r[6],
            }
            for r in rows
        ]
        