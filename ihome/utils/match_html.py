# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/11/13 9:24


from werkzeug.routing import BaseConverter

class ReConverter(BaseConverter):
    def __init__(self,map,regx):
        super(ReConverter, self).__init__(map)
        self.regex = regx