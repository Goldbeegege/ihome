# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/9/26 8:32

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
import settings
import logging
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()
from ihome.utils.match_html import ReConverter
from . views import api #蓝图的导入必须是在SQLAlchemy示例化之后，以防循环导入
from .views .render_html import rh

import os
BASE_DIR = os.path.dirname(__file__)

# 配置日志信息
logging.basicConfig(level=logging.INFO)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler(BASE_DIR + "/logs/logs", maxBytes=1024 * 1024 * 100, backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日记录器
logging.getLogger().addHandler(file_log_handler)
# 设置日志的记录等级



def create_app():
    app = Flask(__name__)
    app.config.from_object(settings.ProductionConfig)
    app.url_map.converters["re"] = ReConverter
    app.register_blueprint(rh)
    app.register_blueprint(api)
    db.init_app(app)
    Session(app)
    CSRFProtect(app) #防止csrf攻击

    return app
