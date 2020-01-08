# -*-coding:utf-8-*- 
# @Email:jinfengxuancheng@163.com 
# @Author: JinFeng 
# @Date: 2019-12-10 20:29:20 
import hashlib
from flask import current_app,session,jsonify,redirect
from functools import wraps
import datetime

def encryption(password):
    secret_key = current_app.config.get("SECRET_KEY")
    ha = hashlib.sha1(bytes(password, encoding="utf-8"))
    ha.update(bytes(secret_key, encoding="utf-8"))
    return ha.hexdigest()

def login_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if session.get("user_id"):
            return func(*args,**kwargs)
        return jsonify(error="用户未登录",msg=302)
    return wrapper

def format_date(d):
    try:
        ret = datetime.datetime.strptime(d, "%Y-%m-%d")
    except Exception as e:
        ret = None
    return ret