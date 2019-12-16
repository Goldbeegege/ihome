import redis

conn = redis.Redis()
# conn.lpush("name",*["jin","xiaosong","xiaohuang"])
print(conn.lrange("name1",0,-1))
# print(conn.get("name"))
l = []
l.insert()