# -*-coding:utf-8-*-
# @author: JinFeng
# @E-mail:jinfengxuancheng@163.com
# @date: 2020/1/9 16:38

from alipay import AliPay
import os


class PayTool(object):
    @property
    def pay(self):
        with open(os.path.join(os.path.dirname(__file__), "keys", "app_private_key.pem"), "r") as f:
            app_private_key_string = f.read()
        with open(os.path.join(os.path.dirname(__file__), "keys", "alipay_public_key.pem"), "r") as f:
            alipay_public_key_string = f.read()
        print("ok")
        alipay = AliPay(
                appid="2016101900725640",
                app_notify_url=None,  # 默认回调url
                app_private_key_string=app_private_key_string,
                # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
                alipay_public_key_string=alipay_public_key_string,
                sign_type="RSA2",  # RSA 或者 RSA2
                debug=True  # 默认False
            )
        return alipay

pay = PayTool().pay