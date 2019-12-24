# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/12/24 16:38

from . import api
from ..utils.commons import login_required
from flask import current_app,jsonify,request,session,make_response,Response
from ihome import db
from .. import models
from ihome.views import constant
import json

@api.route("/my_house")
@login_required
def my_house():
    if session.get("is_auth"):
        return jsonify(error="",msg=1)
    return jsonify(error="没有进行实名认证",msg=0)

@api.route("/area_info")
@login_required
def area_info():
    redis = current_app.config.get("SESSION_REDIS")
    try:
        area_data = redis.get("area_pulic_info")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error="数据库错误",msg=0)
    else:
        if area_data:
            return jsonify(error="",msg=1,data=json.loads(area_data))
    try:
        areas = models.District.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error="数据库错误",msg=0)
    else:
        area_li = []
        for area in areas:
            area_li.append(area.to_dict())
        try:
            redis.setex("area_pulic_info",30*60,json.dumps(area_li))
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(error="数据库错误",msg=0)
        return jsonify(error="",msg=1,data=area_li)
