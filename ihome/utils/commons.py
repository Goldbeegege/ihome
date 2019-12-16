# -*-coding:utf-8-*- 
# @Email:jinfengxuancheng@163.com 
# @Author: JinFeng 
# @Date: 2019-12-10 20:29:20 
import hashlib
from flask import current_app

def encryption(password):
    secret_key = current_app.config.get("SECRET_KEY")
    ha = hashlib.sha1(bytes(password, encoding="utf-8"))
    ha.update(bytes(secret_key, encoding="utf-8"))
    return ha.hexdigest()