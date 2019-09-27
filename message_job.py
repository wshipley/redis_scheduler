import redis
import json

redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)

ps = redis_db.pubsub()
ps.subscribe(['default'])
#
# rc.publish('foo', 'hello world')
#

message = {"job": "url", "url": "newegg.com", "queuework": "True"}


def publishblah(redismessage):
    redis_db.publish('default', json.dumps(redismessage))


publishblah(redismessage=message)
