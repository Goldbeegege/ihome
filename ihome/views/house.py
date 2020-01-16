# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/12/24 16:38

from . import api
from ..utils.commons import login_required,format_date
from .. utils.pagination import XadminPagintor
from flask import current_app,jsonify,request,session
from ihome import db
from .. import models
from ihome.views import constant
import json
from hashlib import md5
import os
from sqlalchemy import or_


@api.route("/my_house")
@login_required
def my_house():
    if not session.get("is_auth"):
        return jsonify(error="没有进行实名认证", msg=0)
    page = request.args.get("page",1)
    user_id = session["user_id"]
    total_length = models.House.query.filter_by(user_id=user_id).count()
    data = {}
    offset = 0
    if total_length > constant.ITEM_PER_PAGE:
        paginator = XadminPagintor(total_length=total_length,amount_per_page=constant.ITEM_PER_PAGE,display_pages=5,current_page=page)
        pages = [i for i in paginator.page_num()]
        offset = (paginator.current_page-1)*constant.ITEM_PER_PAGE
        data["pages"] = pages
        data["page_info"] = {"current_page":paginator.current_page,"start_page":pages[0],"end_page":pages[-1]}
    house_li  = []
    try:
        houses_data =  models.House.query.filter_by(user_id = user_id).order_by(models.House.id.desc()).offset(offset).limit(constant.ITEM_PER_PAGE).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error="数据库错误",msg=0)
    for house in houses_data:
        if house.index_image_url:
            house_li.append(house.format_house_info())
    data["houses"] = house_li
    return jsonify(error="",msg=1,data=data)

@api.route("/area_info")
def area_info():
    redis = current_app.config.get("SESSION_REDIS")
    try:
        area_data = redis.get("area_pulic_info")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error="数据库错误",msg=0)
    if area_data:
        return '{"error":"","msg":1,"data":%s}'%area_data.decode(),200,{"Content-Type":"application/json"}
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
        return jsonify(error="请先进行实名认证",msg=0)
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
    user_id = session["user_id"]
    house = models.House(
        user_id = user_id,
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
    facility = request.form.getlist("facility[]")
    if facility:
        try:
            facility_li = models.Facility.query.filter(models.Facility.id.in_(facility)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(error="数据库错误",msg=0)
        house.facilities = facility_li
    current_app.house = house
    return jsonify(error="",msg=1)

@api.route("/upload_house_image",methods=["POST"])
@login_required
def upload_house_image():
    if not session.get("is_auth"):
        return jsonify(error="请先进行实名认证",msg=0)
    try:
        house = current_app.house
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error="请先完善房源信息",msg=0)
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error="数据库错误",msg=0)
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
            image.seek(0,0)
            image.save(os.path.join(base_dir,file_md5))
        if index == 0:
            house.index_image_url = file_md5
        house_image = models.HouseImage(house_id=house.id,url=file_md5)
        db.session.add(house_image)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(error="数据库错误",msg=0)
    return jsonify(error="",msg=1)

@api.route("/get_house_image")
def get_house_image():
    house_id = request.args.get("house_id")
    if not  house_id:
        return jsonify(error="非法请求",msg=0)
    images = models.HouseImage.query.filter_by(house_id=house_id).all()
    images_li = []
    for image in images:
        images_li.append("/media?file_md5=" + image.url)
    return jsonify(error="",msg=0,data=images_li)

@api.route("/public_house_info")
def public_house_info():
    house_id = request.args.get("house_id")
    if not house_id:
        return jsonify(error="非法请求",msg=0)
    user_id = session.get("user_id")
    #用户未登录，成功返回状态码2
    if not user_id:
        try:
            house = models.House.query.filter_by(id=house_id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(error="数据库错误",msg=0)
        data = house.format_house_info()
        return jsonify(error="",msg=2,data=data)
    #用户已经登录，并且查询的是自己的房源
    try:
        house = models.House.query.filter_by(id=house_id).first()
    except Exception as e:
        current_app.logger(e)
        return jsonify(error="数据库错误",msg=0)
    ret = {"error": "", "msg":2}
    if user_id == house.user_id:
        ret["msg"] = 1
    data = house.format_house_info()
    ret["data"] = data
    return jsonify(**ret)

@api.route("/index")
def index_info():
    try:
        houses = models.House.query.order_by(models.House.order_count.desc()).limit(5).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error="数据库错误",msg=0)
    house_li = []
    for house in houses:
        house_li.append(house.format_house_info())
    return jsonify(error="",msg=0,data=house_li)

@api.route("/houses")
def houses():
    area_id = request.args.get("aid")
    start_date = request.args.get("sd")
    end_date = request.args.get("ed")
    sort_key =  request.args.get("sk")
    page = request.args.get("p",1)
    params = []
    try:
        area_id = int(area_id)
    except Exception as e:
        current_app.logger.error(e)
    else:
        params.append(models.House.area_id == area_id)

    start_date = format_date(start_date)
    end_date = format_date(end_date)
    if start_date and end_date:
        assert start_date <= end_date,"非法时间格式"
        orders = models.Order.query.filter(models.Order.begin_date <= end_date,models.Order.end_date>=start_date,or_(models.Order.status.in_(["WAIT_ACCEPT","WAIT_PAYMENT","PAID","WAIT_COMMENT","COMPLETE"])))
    elif start_date and end_date is None:
        orders = models.Order.query.filter(models.Order.begin_date <= start_date,models.Order.end_date>=start_date,or_(models.Order.status.in_(["WAIT_ACCEPT","WAIT_PAYMENT","PAID","WAIT_COMMENT","COMPLETE"])))
    elif start_date is None and end_date:
        orders = models.Order.query.filter(models.Order.begin_date <= end_date,models.Order.end_date>=end_date,or_(models.Order.status.in_(["WAIT_ACCEPT","WAIT_PAYMENT","PAID","WAIT_COMMENT","COMPLETE"])))
    else:
        orders = []
    orders_li = [order.house_id for order in orders]
    params.append(models.House.id.notin_(orders_li))
    try:
        current_page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        current_page = 1
    try:
        if sort_key == "booking":
            paginator = models.House.query.filter(*params).order_by(models.House.order_count.desc()).paginate(page=current_page,per_page=constant.SEARCH_DISPLAY_ITEMS,error_out=False)
        elif sort_key == "price-inc":
            paginator = models.House.query.filter(*params).order_by(models.House.price.asc()).paginate(page=current_page,per_page=constant.SEARCH_DISPLAY_ITEMS,error_out=False)
        elif sort_key == "price-des":
            paginator = models.House.query.filter(*params).order_by(models.House.price.desc()).paginate(page=current_page,per_page=constant.SEARCH_DISPLAY_ITEMS,error_out=False)
        else:
            paginator = models.House.query.filter(*params).order_by(models.House.create_time.desc()).paginate(page=current_page,per_page=constant.SEARCH_DISPLAY_ITEMS,error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error="数据库错误",msg=0)
    house_data = [house.format_house_info() for house in paginator.items]
    return jsonify(error="",msg=1,data={"total_page":paginator.pages,"houses":house_data})

@api.route("/comments")
def comments():
    house_id = request.args.get("house_id")
    if not  house_id:
        return jsonify(error="非法请求",msg=0)
    orders = models.Order.query.filter_by(house_id=house_id).all()
    order_data = [order.to_dict() for order in orders]
    return jsonify(error="",msg=0,data=order_data)