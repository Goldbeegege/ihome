# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/9/26 8:34






from flask import Blueprint
from .. import models

api = Blueprint("api",__name__)

from . import users, house