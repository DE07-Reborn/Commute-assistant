import json

class RedisRoute:
    '''
        Util class for put and get data into/from redis
    '''
    def __init__(self, redis_client):
        self.redis = redis_client

    def _key(self, user_id:str):
        '''
            create key by user id
            param
                user_id : User's unique ID
        '''
        return f'route:state:{user_id}'
    
    def get(self, user_id:str):
        '''
            Get data if exists from key composed of userID
            param
                user_id : User's unique ID
        '''
        data = self.redis.get(self._key(user_id))
        return json.loads(data) if data else None
    

    def set(self, user_id:str, payload:dict):
        """
            insert data(payload) into redis with its userID's key
            param
                user_id : User's unique ID
                payload : the data as json of route data
        """
        self.redis.set(
            self._key(user_id),
            json.dumps(payload),
            ex = 60 * 60 # TTL : 1 hour
        )