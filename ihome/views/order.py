# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2020/1/6 19:41
from . import api
from ..utils.commons import login_required,format_date
from flask import current_app,jsonify,request,session
from ihome import db
from .. import models


@api.route("/book", methods=["GET", "POST"])
@login_required
def book():
    house_id = request.args.get("house_id")
    if not house_id:
        return jsonify(error="非法请求", msg=0)
    try:
        house_obj = models.House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error="数据库错误", msg=0)
    if not house_obj:
        return jsonify(error="房源不存在", msg=0)

    if request.method == "GET":
        return jsonify(error="", msg=1, data=house_obj.format_house_info())
    elif request.method == "POST":
        user_id = session.get("user_id")
        if user_id == house_obj.user_id:
            return jsonify(error="禁止刷单", msg=0)
        sd = request.form.get("start_date")
        ed = request.form.get('end_date')
        start_date = format_date(sd)
        end_date = format_date(ed)
        if not all([start_date, end_date]):
            return jsonify(error="请选择完整日期范围", msg=0)
        assert start_date <= end_date, "入住日期不合法"
        days = (end_date - start_date).days + 1
        if days > house_obj.max_days or days < house_obj.min_days:
            return jsonify(error="您选择入住%s，但最少入住%s天,最多入住%s天" % (days, house_obj.min_days, house_obj.max_days))
        amount = request.form.get("amount")
        if not amount:
            return jsonify(error="无法校验金额", msg=0)
        try:
            amount = int(amount)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(error="传入金额不正确", msg=0)
        backend_amount = days * int(house_obj.price)
        if amount != backend_amount:
            return jsonify(error="前后端金额不一致", msg=0)
        try:
            order = models.Order.query.filter(models.Order.house_id == house_id, models.Order.begin_date <= end_date,
                                              models.Order.end_date >= start_date).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(error="数据库错误", msg=0)
        if order:
            return jsonify(error="该时间段房间已被预定", msg=0)
        new_order = models.Order(
            user_id=user_id,
            house_id=house_id,
            begin_date=start_date,
            end_date=end_date,
            days=days,
            house_price=house_obj.price,
            amount=backend_amount
        )

        try:
            db.session.add(new_order)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(error="数据库错误",msg=0)
        return jsonify(error="", msg=1)

@api.route("/order_info")
@login_required
def order_info():
    order_type= request.args.get("type")
    if not order_type:
        return jsonify(error="参数不完整",msg=0)
    user_id = session.get("user_id")
    try:
        if order_type == "0":
            orders = models.Order.query.filter_by(user_id=user_id).order_by(models.Order.create_time.desc()).all()
        elif order_type == "1":
            houses = models.House.query.filter_by(user_id=user_id).all()
            orders = models.Order.query.filter(models.Order.house_id.in_([house.id for house in houses])).order_by(models.Order.create_time.desc()).all()
        else:
            orders = []
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error="数据库错误",msg=0)
    order_li = [order.to_dict() for order in orders if orders]
    return jsonify(error="",msg=1,data=order_li)

@api.route("/status",methods=["PUT","POST"])
@login_required
def status():
    order_id = request.form.get("order_id")
    if request.method == "PUT":
        if not order_id:
            return jsonify(error="非法请求",msg=0)
        update_data = {"status": "WAIT_PAYMENT"}
    elif request.method == "POST":
        comment = request.form.get("comment")
        if not all([order_id,comment]):
            return jsonify(error="非法请求",msg=0)
        update_data = {"status": "REJECTED", "comment": comment}
    landlord_id = session.get("user_id")
    try:
        houses = models.House.query.filter_by(user_id=landlord_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error="数据库错误",msg=0)
    if not houses:
        return jsonify(error="该订单对应的房源不存在",msg=0)
    try:
        models.Order.query.filter(models.Order.house_id.in_([house.id for house in houses]),models.Order.id==order_id,models.Order.status=="WAIT_ACCEPT").update(update_data,synchronize_session=False)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error="数据库错误",msg=0)
    return jsonify(error="",msg=1,data={"order_id":order_id})
