# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/9/26 8:30
import redis


class BaseConfig(object):
    SECRET_KEY = "jdklj#$@JKjkl%$"

    #关于flask_sqlalchemy的配置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:jin001@127.0.0.1:3306/ihome?charset=utf8"
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_MAX_OVERFLOW = 5
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #关于flask_session的配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.Redis(host='127.0.0.1', port='6379')


class DevConfig(BaseConfig):
    Debug = True


class ProductionConfig(BaseConfig):
    Debug = False
