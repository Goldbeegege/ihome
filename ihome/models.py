# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/11/11 17:08


from datetime import datetime
from . import db


class BaseModel(object):
    create_time = db.Column(db.DateTime,default=datetime.now)
    update_time = db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now)

class User(BaseModel,db.Model):
    """用户信息表"""
    __tablename__= "ihome_user_profile"

    id = db.Column(db.Integer,primary_key=True) #用户编号
    nick_name = db.Column(db.String(32),unique=True,nullable=False) #用户昵称
    password_hash = db.Column(db.String(128),nullable=False) #用户密码，密文
    mobile_num = db.Column(db.String(11), default="")
    real_name = db.Column(db.String(32))  # 真实姓名
    id_card = db.Column(db.String(20))  # 身份证号
    avatar_url = db.Column(db.String(128))  # 用户头像路径
    houses = db.relationship("House", backref="user")  # 用户发布的房屋
    orders = db.relationship("Order", backref="user")  # 用户下的订单


class District(BaseModel,db.Model):
    """城区"""
    __tablename__ = "ihome_area_info"

    id = db.Column(db.Integer, primary_key=True)  # 区域编号
    name = db.Column(db.String(32), nullable=False)  # 区域名字
    houses = db.relationship("House", backref="area")  # 区域的房屋

    def to_dict(self):
        return {
            "id":self.id,
            "name":self.name
        }

house_facility = db.Table(
    "ihome_house_facility",
    db.Column("house_id",db.Integer,db.ForeignKey("ihome_house_info.id"),primary_key=True),
    db.Column("facility_id",db.Integer,db.ForeignKey("ihome_facility_info.id"),primary_key=True),
)

class House(BaseModel,db.Model):
    """房屋信息"""
    __tablename__ = "ihome_house_info"

    id = db.Column(db.Integer, primary_key=True)  # 房屋编号
    user_id = db.Column(db.Integer, db.ForeignKey("ihome_user_profile.id"), nullable=False)  # 房屋主人的用户编号
    area_id = db.Column(db.Integer, db.ForeignKey("ihome_area_info.id"), nullable=False)  # 归属地的区域编号
    title = db.Column(db.String(64), nullable=False)  # 标题
    price = db.Column(db.Integer, default=0)  # 单价，单位：分
    address = db.Column(db.String(512), default="")  # 地址
    room_count = db.Column(db.Integer, default=1)  # 房间数目
    acreage = db.Column(db.Integer, default=0)  # 房屋面积
    unit = db.Column(db.String(32), default="")  # 房屋单元， 如几室几厅
    capacity = db.Column(db.Integer, default=1)  # 房屋容纳的人数
    beds = db.Column(db.String(64), default="")  # 房屋床铺的配置
    deposit = db.Column(db.Integer, default=0)  # 房屋押金
    min_days = db.Column(db.Integer, default=1)  # 最少入住天数
    max_days = db.Column(db.Integer, default=0)  # 最多入住天数，0表示不限制
    order_count = db.Column(db.Integer, default=0)  # 预订完成的该房屋的订单数
    index_image_url = db.Column(db.String(256), default="")  # 房屋主图片的路径
    facilities = db.relationship("Facility", secondary=house_facility)  # 房屋的设施
    images = db.relationship("HouseImage")  # 房屋的图片
    orders = db.relationship("Order", backref="house")  # 房屋的订单

    def format_house_info(self):
        return {
            "order_count":self.order_count,
            "house_id":self.id,
            "house_lord":self.user.nick_name,
            "area":self.area.name,
            "title":self.title,
            "price":int(self.price/100.00),
            "address":self.address,
            "room_count":self.room_count,
            "acreage":self.acreage,
            "unit":self.unit,
            "capacity":self.capacity,
            "beds":self.beds,
            "deposit":int(self.deposit/100.00),
            "min_days":self.min_days,
            "max_days":self.max_days if int(self.max_days) != 0 else "无限制",
            "update_time":self.create_time.strftime("%Y-%m-%d %H:%M"),
            "index_image_url":"/media?file_md5="+self.index_image_url,
            "landlord_pic":"/media?file_md5="+self.user.avatar_url if self.user.avatar_url else "/static/images/default.png",
            "facilities":[{"name":f.name,"icon":f.icon} for f in self.facilities]
        }

class Facility(BaseModel, db.Model):
    """设施信息"""

    __tablename__ = "ihome_facility_info"

    id = db.Column(db.Integer, primary_key=True)  # 设施编号
    name = db.Column(db.String(32), nullable=False)  # 设施名字
    icon = db.Column(db.String(32),nullable=False) #设施在前端生成的样式


class HouseImage(BaseModel, db.Model):
    """房屋图片"""

    __tablename__ = "ihome_house_image"

    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey("ihome_house_info.id"), nullable=False)  # 房屋编号
    url = db.Column(db.String(256), nullable=False)  # 图片的路径


class Order(BaseModel, db.Model):
    """订单"""

    __tablename__ = "ihome_order_info"

    id = db.Column(db.Integer, primary_key=True)  # 订单编号
    user_id = db.Column(db.Integer, db.ForeignKey("ihome_user_profile.id"), nullable=False)  # 下订单的用户编号
    house_id = db.Column(db.Integer, db.ForeignKey("ihome_house_info.id"), nullable=False)  # 预订的房间编号
    begin_date = db.Column(db.DateTime, nullable=False)  # 预订的起始时间
    end_date = db.Column(db.DateTime, nullable=False)  # 预订的结束时间
    days = db.Column(db.Integer, nullable=False)  # 预订的总天数
    house_price = db.Column(db.Integer, nullable=False)  # 房屋的单价
    amount = db.Column(db.Integer, nullable=False)  # 订单的总金额
    trade_no = db.Column(db.String(80))
    status = db.Column(  # 订单的状态
        db.Enum(
            "WAIT_ACCEPT",  # 待接单,
            "WAIT_PAYMENT",  # 待支付
            "PAID",  # 已支付
            "WAIT_COMMENT",  # 待评价
            "COMPLETE",  # 已完成
            "CANCELED",  # 已取消
            "REJECTED"  # 已拒单
        ),
        default="WAIT_ACCEPT", index=True)
    comment = db.Column(db.Text)  # 订单的评论信息或者拒单原因

    def to_dict(self):
        return {
            "house_id":self.house_id,
            "order_id":self.id,
            "username":self.user.nick_name,
            "comment_time":self.create_time,
            "begin_date":self.begin_date.strftime("%Y-%m-%d"),
            "end_date":self.end_date.strftime("%Y-%m-%d"),
            "days":self.days,
            "house_price":self.house_price,
            "amount":self.amount,
            "status":self.status,
            "comment":self.comment_handler(),
            "img_url":"/media?file_md5="+self.house.index_image_url,
            "title":self.house.title,
            "ctime":self.create_time.strftime("%Y-%m-%d %H:%M")
        }

    def comment_handler(self):
        if not self.comment:
            return  self.comment
        if len(self.comment) > 10:
            return "<a href = 'javascript:;' comment-id='%s'>查看详情</a>"%self.id
        return self.comment