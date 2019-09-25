import redis
redis_db = redis.Redis()

ps = redis_db.pubsub()
ps.subscribe(['default'])
#
for item in ps.listen():
    if item['type'] == 'message':
        print(item['data'])



