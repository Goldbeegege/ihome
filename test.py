# -*-coding:utf-8-*-
# @author: JinFeng
# @e-mail: jinfengxuancheng@163.com
# @date: 2019/12/22 11:06 上午


import redis
conn = redis.Redis()
print(conn.keys())
conn.incr("jinfeng")
conn.delete("jinfeng")
print(conn.keys())
