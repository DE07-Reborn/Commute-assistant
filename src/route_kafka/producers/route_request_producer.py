from kafka import KafkaProducer
import json
from datetime import datetime
import uuid

class RouteRequestProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers="kafka:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda v: v.encode("utf-8"),
        )


    def send_topic(self, user_id:str, request_info:dict):
        """
            Call request api then send its json data to kafka topic
            param
                user_id : user's unique id
                request_info : information dictionary for data
        """
        payload = {
            "request_id": str(uuid.uuid4()),
            "user_id": user_id,
            "origin": {
                "lat": request_info["home_address"][1],
                "lon": request_info["home_address"][0],
            },
            "destination": {
                "lat": request_info["work_address"][1],
                "lon": request_info["work_address"][0],
            },
            "arrive_by": request_info["arrival_time"].isoformat(),
            "feedback_time_sec": request_info["feedback_time"] * 60,
            "produced_at": datetime.now().isoformat(),
        }

        self.producer.send(
            topic="route_request",
            key=user_id,
            value=payload,
        )
        
        self.producer.flush()
        return payload["request_id"]
