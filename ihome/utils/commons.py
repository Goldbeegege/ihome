# -*-coding:utf-8-*- 
# @Email:jinfengxuancheng@163.com 
# @Author: JinFeng 
# @Date: 2019-12-10 20:29:20 
import hashlib
from flask import current_app,session,jsonify,request
from functools import wraps
from hashlib import md5

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
        return jsonify(error="用户未登录",msg=0)
    return wrapper