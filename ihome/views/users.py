# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/11/14 9:09


from . import api
from ..utils.captcha import Create_Validation_Code
from ..utils.commons import encryption,login_required
from ..utils.response_code import RET
from io import BytesIO
from flask import current_app,jsonify,request,session,make_response,Response
from geetest import GeetestLib
from ihome import db
from .. import models
import re
from ihome.views import constant
import time
import os
from hashlib import md5
import json


@api.route("/image_code/<string:imageNo>")
def image_code(imageNo):
    """
    专门用于向前端返验证码；
    imageNo:str 随机字符串，为redis中查询验证码的“键”
    """
    #获取redis对象，准备使用redis数据库
    #将图片转换成二进制形式
    redis = current_app.config.get("SESSION_REDIS")
    stream = BytesIO()
    text, img = Create_Validation_Code().generate_code()
    img.save(stream, "PNG")  # 将验证码保存在内存中
    try:
        #将生成的验证码文字存在redis中，并设置过期时间为180秒
        redis.setex(imageNo,constant.IMAGE_CODE_EXPIRED_TIME,text)
    except Exception as e:
        current_app.logger.error(str(e) + " redis保存错误")
        return jsonify(**{"errorno":RET.DBERR,"msg":"数据库保存错误"})
    return stream.getvalue()

@api.route("/pc-geetest/register")
def pcgetcaptcha():
    """
    行为验证码的首次验证，来获取用户已授权的id与key
    """
    user_id = 'test'
    gt = GeetestLib(constant.pc_geetest_id, constant.pc_geetest_key)
    status = gt.pre_process(user_id)
    session[gt.GT_STATUS_SESSION_KEY] = status
    session["user_id"] = user_id
    response_str = gt.get_response_str()
    return response_str

@api.route("/pc-geetest/ajax_validate",methods=["POST"])
def pcajax_validate():
    """
    行为验证的二次验证，同时也是注册信息的校验
    只允许使用post的方式进行提交

    注册所需参数：
    username:str 用户名
    password:str 密码
    imagecode:str 验证码
    imageId:str 用户获取redis中存储的验证码的“键”
    """
    redis = current_app.config.get("SESSION_REDIS")
    ret = {"error": None, "msg": None}
    gt = GeetestLib(constant.pc_geetest_id, constant.pc_geetest_key)
    challenge = request.form.get(gt.FN_CHALLENGE, '')
    validate = request.form.get(gt.FN_VALIDATE, '')
    seccode = request.form.get(gt.FN_SECCODE, '')
    status = session[gt.GT_STATUS_SESSION_KEY]
    user_id = session["user_id"]
    if status:
        result = gt.success_validate(challenge, validate, seccode, user_id)
    else:
        result = gt.failback_validate(challenge, validate, seccode)
    if result:
        #行为验证码校验成功，返回1，失败返回0
        #获取注册有需要的参数
        password = request.form.get("password")
        password2 = request.form.get("password2")
        mobile_num = request.form.get("mobile")
        imageId = request.form.get("imageId")
        imagecode = request.form.get("imagecode")
        username = request.form.get("username")

        #校验参数的完整性
        if not all([password,password2,imagecode,imageId,user_id,mobile_num]):
            ret["error"] = "请将个人信息填写完整"
            ret["msg"] = "all"
            return jsonify(ret)
        
        #获取验证码
        redis_image_code = redis.get(imageId)
        #若没有获取到，则可能：验证码超时过期了；或数据库链接出问题了，统一返回验证码过期的错误
        if redis_image_code is None: 
            ret["msg"] = "imagecode"
            ret["error"] = "验证码已过期"
            return ret
        #获取到验证码后立即删除，保证每次访问不管验证码有没有输入正确，下一次都会是不同的验证码。以防暴力测试
        redis.delete(imageId)
        #校验验证码，不区分大小写
        if bytes(imagecode,encoding="utf-8").upper() != redis_image_code.upper():
            ret["msg"] = "imagecode"
            ret["error"] = "验证码错误"
            return ret
        #初步检验两次秘密是否一致，若两次密码输入不一致，则没有必要在去判断密码输入的格式是否正确
        if password != password2:
            ret["error"] = "两次密码输入不一致"
            ret["msg"] = "password"
            return ret          
        
        #逐步校验用户名和密码格式是否正确
        val = ValideInfo(**{"username": username, "password": password,"mobile":mobile_num})
        ret = val.validate()
        if ret.get("error"):
            return ret
        #在通过参数校验后，加密密码，将该用户信息写入数据库
        password = encryption(password)
        user_obj = models.User(nick_name=username,password_hash=password,mobile_num=mobile_num)
        db.session.add(user_obj)
        #改变数据库的操作需要进行提交
        db.session.commit()
        return ret
    ret["error"] = "未知错误"
    ret["msg"] = "unknown"
    return jsonify(ret)

class ValideInfo(object):
    """
    校验用户名与密码的格式
    """
    def __init__(self,**kwargs):
        self.arguments = kwargs
        self.ret = {"error":"","msg":""}
    
    def validate(self):
        """
        将要校验的参数获取到通过反射的方式逐个验证
        这种方式模仿Django中的钩子函数，方便以后添加参数时的扩展
        """
        for key, value in self.arguments.items():
            if hasattr(self, "valide_"+key):
                ret = getattr(self, "valide_"+key)(value)
                if ret.get("error"):
                    return ret
                continue
            raise Exception("method `{}` not found".format("valide_"+key)) 
        return self.ret   
    def valide_username(self,value):     
        """
        钩子函数，用于校验用户名
        """   
        if not re.search(r"[0-9a-zA-Z_]{6,12}", value):
            self.ret["error"] = "用户名由数字字母或下划线组成，长度为6-12个字符"
            self.ret["msg"] = "username"
            return self.ret
        user = models.User.query.filter_by(nick_name=value).first()
        if not user:
            return self.ret
        #已查询到记录，需要校验该条记录是否属于该用户本身
        username = session.get("username")
        if username:
            if user.nick_name == value and value != username:
                self.ret["error"] = "用户名已存在"
                self.ret["msg"] = "username"
                return self.ret
            return self.ret
        #注册时查询到了user记录表示该用户名已经存在
        self.ret["error"] = "用户名已存在"
        self.ret["msg"] = "username"
        return self.ret

    def valide_password(self,value):
        if not re.findall(".{8,16}",value):
            self.ret["error"] = "密码长度为8-16个字符"
            self.ret["msg"] = "password"
        return self.ret

    def valide_mobile(self,value):
        if not re.search(r"1[3578]\d{9}",value):
            self.ret["error"] = "非法手机号码"
            self.ret["msg"] = "mobile"
            return self.ret
        return self.ret

    def valide_id_card(self,value):
        if re.search(r"^[1-9]\d{5}(18|19|20|(3\d))\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$",value):
            return self.ret
        self.ret["error"] = "非法身份证号"
        self.ret["msg"] = "id-card"
        return self.ret

    def valide_real_name(self,value):
        if re.match(r"^[\u4e00-\u9fa5][\u4e00-\u9fa5]*[\u4e00-\u9fa5]$",value):
            return self.ret
        self.ret["error"] = "名字好奇怪"
        self.ret["msg"] = "real-name"
        return self.ret

@api.route("/session",methods=["POST"])
def signup():
    username = request.get_json().get("username")
    password = request.get_json().get("password")
    print(username,password)
    if not all([username,password]):
        return jsonify(error="信息填写不完整",msg="all")
    user_ip = request.remote_addr
    if not control_request_times(user_ip):
        return jsonify(error="请求次数过于频繁，请稍后重试",msg="all")
    user = models.User.query.filter_by(nick_name=username,password_hash=encryption(str(password))).first()
    if not user:
        return jsonify(error="用户名或密码错误",msg="0")
    session["user_id"] = user.id
    session["username"] = user.nick_name
    session["file_md5"] = user.avatar_url if user.avatar_url else ""
    session["mobile"] = user.mobile_num
    if user.real_name and user.id_card:
        session["is_auth"] = True
    else:
        session["is_auth"] = False
    response = make_response(jsonify(error="",msg=""))
    return response 

def control_request_times(value,interval=constant.TIME_SPAN,times=constant.TIMES):
    ctime = time.time()
    request_times = session.get("frequency_times_%s"%value)
    if request_times is None:
        session["frequency_times_%s"%value] = [ctime]
    elif len(request_times) < times:
        session["frequency_times_%s"%value].insert(0,ctime)
    else:
        if ctime - request_times[-1] < interval:
            return False
        request_times.pop()
        request_times.insert(0,ctime)
    return True

@api.route("/session")
def get_login_info():
    if session.get("user_id"):
        return jsonify(error="",msg="ok",data = {"username":session.get("username"),"user_id":session.get("user_id")})
    else:
        return jsonify(error="用户未登录",msg="0")

@api.route("/logout")
def logout():
    session.clear()
    return jsonify(error="",msg=1)

@api.route("/my_info")
@login_required
def my_info():
    data = {
        "user_id":session.get("user_id"),
        "username":session.get("username"),
        "mobile": session["mobile"]
    }
    return jsonify(error="",data=data,msg=1)


@api.route("/upload_avatar",methods=["POST"])
@login_required
def upload_avatar():
    if not control_request_times(session["user_id"],interval=60,times=3):
        return jsonify(error="上传次数过于频繁，请稍后再试",msg=0)
    base_dir = current_app.config.get("ROOT")
    file_obj = request.files.get("avatar")
    if not file_obj:
        return jsonify(error="请上传图片",msg=0)
    content = file_obj.read()
    md = md5(content)
    file_md5 = md.hexdigest()
    file_md5 = file_md5 +"."+ file_obj.filename.rsplit(".",1)[1]
    user_avatar_md5 = session.get(file_md5)
    if not user_avatar_md5 or user_avatar_md5 != file_md5:
        try:
            models.User.query.filter_by(id=session.get("user_id")).update({"avatar_url":file_md5})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(error="数据库异常,请稍后再试",msg=0)
        if file_md5 not in os.listdir(base_dir):
            with open(os.path.join(base_dir, file_md5),"wb") as f:
                f.write(content)
        try:
            os.rmdir(os.path.join(base_dir, file_md5))
        except Exception as e:
            pass
    session["file_md5"] = file_md5
    redis = current_app.config["SESSION_REDIS"]
    redis.incr("avatar_upload_time")
    return jsonify(error="", msg=1,data={"file_md5":file_md5})

@api.route("/media")
def media():
    file_md5 = request.args.get("file_md5")
    if not file_md5:
        file_md5 = session.get("file_md5")
        if not file_md5:
            return jsonify(error="非法请求",msg=0)
    base_dir = current_app.config.get("ROOT")
    if file_md5 in os.listdir(base_dir):
        with open(os.path.join(base_dir,file_md5),"rb") as f:
            file_obj = f.read()
        response = Response(file_obj,mimetype="image/*")
        return response
    return jsonify(error="图片请求错误",msg=0)

@api.route("/change_username")
@login_required
def change_username():
    redis = current_app.config.get("SESSION_REDIS")
    try:
        if redis.get("%s_usename_chage"%session["user_id"]):
            return jsonify(error="七天内只能修改一次用户名",msg=0)
    except Exception as e:
        current_app.logger.error(e)
    username = request.args.get("username")
    val = ValideInfo(username=username)
    ret = val.validate()
    if ret.get("error"):
        return ret
    try:
        models.User.query.filter_by(id=session["user_id"]).update({"nick_name":username})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error="数据库异常，请稍后重试",msg=0)
    session["username"] = username
    try:
        redis.setex("%s_usename_chage"%session["user_id"],constant.USERNAME_EXPIRE_TIME,0)
    except Exception as e:
        current_app.logger.error(e)
    return jsonify(error="",msg=1)

@api.route("/change_mobile")
@login_required
def change_mobile():
    if session.get("mobile"):
        return jsonify(error="不予许随意更改手机号码",msg=0)
    mobile = request.args.get("mobile")
    val = ValideInfo(mobile=mobile)
    ret = val.validate()
    if ret.get("error"):
        return ret
    try:
        models.User.query.filter_by(id=session["user_id"]).update({"mobile_num":mobile})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error="数据库异常，请稍后重试",msg=0)
    session["mobile"] = mobile
    return jsonify(error="",msg=1)

@api.route("/auth",methods=["POST"])
@login_required
def auth():
    real_name = request.form.get("real_name")
    id_card = request.form.get("id_card")
    if not all([real_name,id_card]):
        return  jsonify(error="参数不完整",msg="all")
    val = ValideInfo(real_name=real_name,id_card=id_card)
    ret = val.validate()
    if ret.get("error"):
        return ret
    try:
        user = models.User.query.filter_by(id=session["user_id"],real_name=None,id_card=None).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user:
            user.real_name = real_name
            user.id_card = id_card
            db.session.commit()
            session["is_auth"] = True
            return jsonify(error="",msg=1,data={"real_name":real_name,"id_card":id_card})
        return jsonify(error="实名认证成功，不予许随意改动")
    return jsonify(error="数据异常，请稍后再试",msg=0)

@api.route("/init_auth")
@login_required
def init_auth():
    redis = current_app.config.get("SESSION_REDIS")
    try:
        user_auth =  redis.get("%s_auth"%session["username"])
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error="数据库错误",msg=0)
    else:
        if user_auth:
            return '{"error":"","msg":1,"data":%s}'%user_auth.decode(),200,{"Content-Type":"application/json"}
        try:
            user = models.User.query.filter_by(id=session["user_id"]).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(error="数据库错误",msg=0)
        else:
            ret = {"msg":1,"error":""}
            if user.id_card and user.real_name:
                data = {
                    "id_card":user.id_card,
                    "real_name":user.real_name
                }
                try:
                    redis.setex("%s_auth"%session["username"],30*60,json.dumps(data))
                except Exception as e:
                    current_app.logger.error(e)
                ret["data"] = data
            return jsonify(**ret)