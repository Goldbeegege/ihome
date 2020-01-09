# -*-coding:utf-8-*-
# @author: JinFeng
# @E-mail:jinfengxuancheng@163.com
# @date: 2020/1/9 10:27
from . import api
from ..utils.commons import login_required
from ..utils.pay_tools import pay
from flask import current_app,jsonify,request,session,redirect
from ihome import db
from .. import models


@api.route("/payment/<int:house_id>/<int:order_id>",methods=["PUT"])
@login_required
def alipay_payment(house_id,order_id):
    if not order_id:
        return jsonify(error="非法请求",msg=0)
    user_id = session.get("user_id")
    order = models.Order.query.filter(models.Order.user_id==user_id,models.Order.house_id==house_id,models.Order.status=="WAIT_PAYMENT").first()
    if not order:
        return jsonify(error="订单不存在",msg=0)

    # 手机网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
    order_string = pay.api_alipay_trade_wap_pay(
        out_trade_no=order_id,
        total_amount=order.amount/100.0,
        subject=order.house.title,
        return_url="http://127.0.0.1:5000/result"
    )
    return jsonify(error="",msg=1,data={"url":"https://openapi.alipaydev.com/gateway.do?" + order_string})

@api.route("/result",methods=["GET","POST"])
@login_required
def result():
    data = request.args.to_dict()
    # sign 不能参与签名验证
    order_id = data.get("out_trade_no")
    if not order_id:
        return jsonify(error="非法请求",msg=0)
    signature = data.pop("sign")
    # verify
    success = pay.verify(data, signature)
    if success:
        try:
            ret = models.Order.query.filter(models.Order.id==order_id,models.Order.status=="WAIT_PAYMENT").update({"status":"PAID","trade_no":data.get("trade_no")},synchronize_session=False)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(error="数据库错误",msg=0)
        if ret == 0:
            return jsonify(error="该订单不存在",msg=0)
        return redirect("/orders")
    return jsonify(error="非法请求",msg=0)