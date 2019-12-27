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
from hashlib import md5
import os

@api.route("/my_house")
@login_required
def my_house():
    if not session.get("mobile"):
        return jsonify(error="没有设置手机号码",msg=0,code=100)
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
    if area_data:
        return jsonify(error="",msg=1,data=json.loads(area_data))
    try:
        areas = models.District.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error="数据库错误",msg=0)
    area_li = []
    for area in areas:
        area_li.append(area.to_dict())
    try:
        redis.setex("area_pulic_info",30*60,json.dumps(area_li))
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error="数据库错误",msg=0)
    return jsonify(error="",msg=1,data=area_li)

@api.route("/public_new_house",methods=["POST"])
@login_required
def public_new_house():
    if not session.get("is_auth"):
        return jsonify(error="q请先进行实名认证",msg=0)
    title = request.form.get("title")
    price = request.form.get("price")
    area_id = request.form.get("area_id")
    address = request.form.get("address")
    room_count = request.form.get("room_count")
    acreage = request.form.get("acreage")
    unit = request.form.get("unit")
    capacity = request.form.get("capacity")
    beds = request.form.get("beds")
    deposit = request.form.get("deposit")
    min_days = request.form.get("min_days")
    max_days = request.form.get("max_days")

    if not all([title,price,area_id,address,room_count,acreage,unit,capacity,beds,deposit,min_days,max_days]):
        return jsonify(error="请填写完房源的基本信息与详细信息 ",msg=0)
    house = models.House(
        user_id = session["user_id"],
        title = title,
        price = int(float(price)*100),
        area_id = area_id,
        address = address,
        room_count = room_count,
        acreage = acreage,
        unit = unit,
        capacity = capacity,
        beds = beds,
        deposit =int(float(deposit)*100),
        min_days = min_days,
        max_days =max_days
    )

    facility = request.form.get("facility")
    if facility:
        try:
            facility_li = models.Facility.query.filter(models.Facility.id.in_(facility)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(error="数据库错误",msg=0)
        house.facilities = facility_li
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
    return jsonify(error="",msg=1,data={"house_id":house.id})

@api.route("/upload_house_image",methods=["POST"])
@login_required
def upload_house_image():
    if not session.get("is_auth"):
        return jsonify(error="q请先进行实名认证",msg=0)
    house_id = request.form.get('house_id')
    if not house_id:
        return jsonify(error="房源不存在",msg=0)
    try:
        house = models.House.query.filter_by(user_id=session["user_id"],id=house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error="身份信息不匹配",msg=0)
    image_li = request.files
    if not image_li:
        return jsonify(error="请上传图片", msg=0)
    for index,image_name in enumerate(image_li):
        image = request.files.get(image_name)
        content = image.read()
        md = md5(content)
        file_md5 = md.hexdigest()
        file_md5 = file_md5 +"."+ image.filename.rsplit(".",1)[1]
        base_dir = current_app.config.get("ROOT")
        if file_md5 not in os.listdir(os.path.join(base_dir)):
            image.save(os.path.join(base_dir,file_md5))
        if index == 0:
            house.index_image_url = file_md5
        house_image = models.HouseImage(house_id=house_id,url=file_md5)
        db.session.add(house_image)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(error="数据库错误",msg=0)
    return jsonify(error="",msg=1,data={"file_md5":""})