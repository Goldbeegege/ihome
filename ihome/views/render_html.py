# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/11/13 9:21

from flask import Blueprint,current_app,make_response
from flask_wtf import csrf

rh = Blueprint("render_page","__name__")

@rh.route("/<re(r'.*'):file_name>")
def get_html(file_name):
    if file_name and file_name != "favicon.ico":
        file_name = "html/"+file_name+".html"
    else:
        file_name = "html/index.html"
    csrf_token = csrf.generate_csrf()
    response = make_response(current_app.send_static_file(file_name))
    response.set_cookie("csrf_token",csrf_token)
    return response

