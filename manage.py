# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/9/26 8:27

from ihome import create_app
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from ihome import db


app = create_app()
manage = Manager(app)

Migrate(app,db)

manage.add_command("db",MigrateCommand)


if __name__ == '__main__':
    manage.run()