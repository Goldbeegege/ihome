# -*-coding:utf-8-*- 
# @Email:jinfengxuancheng@163.com 
# @Author: JinFeng 
# @Date: 2019-12-10 20:34:06 

#验证码过期时间，单位：秒
IMAGE_CODE_EXPIRED_TIME = 180

#行为验证码的测试id与key
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


#访问次数限制间隔时间，单位秒
FREQUENCY_INTERVAL_TIME = 180

#与节流相关
#多长时间间隔内允许访问几次
#时间间隔，单位秒
TIME_SPAN = 60
#次数：
TIMES = 5

#修改一次用户名,7天之后才能再次修改,单位：秒
USERNAME_EXPIRE_TIME = 60*60*24*7

#在展示自己发布的房源是，每页展示几条
ITEM_PER_PAGE = 5

#在搜索页面每页展示几条
SEARCH_DISPLAY_ITEMS = 3