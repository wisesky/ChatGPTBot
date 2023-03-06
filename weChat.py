#! python3
# -*- encoding: utf-8 -*-
'''
@File   : weChat.py
@Time   : 2023/03/06 12:47:13
@Author : Franklin Chen
@Contact: wisesky1988@gmail.com
@Licence: MIT License
@Desc   : 
'''

from datetime import datetime, timedelta
from flask import Flask, jsonify, request, url_for
from weixin import Weixin, WeixinError
from weixin.msg import WeixinMsg


app = Flask(__name__)
app.debug = True

# 初始化微信
weixin = Weixin()
weixin.init_app(app)

# 具体导入配
# 根据需求导入仅供参考
app.config.fromobject(dict(WEIXIN_APP_ID='wx3a9d69fe1255c373', WEIXIN_APP_SECRET='eaa2205021de096728fe01a44755b073', WEIXIN_TOKEN='7c0cd95f55c61fe37e8ed9e27171c2ec'))

# 微信消息
msg = weixin.msg

app.add_url_rule("/", view_func=msg.view_func)


@msg.all
def all(**kwargs):
	"""
	监听所有没有更特殊的事件
	"""
    return msg.reply(kwargs['sender'], sender=kwargs['receiver'], content='all')


@msg.text()
def hello(**kwargs):
	"""
	监听所有文本消息
	"""
    return "hello too"


@msg.text("help")
def world(**kwargs):
	"""
	监听help消息
	"""
    return dict(content="hello world!")

@msg.image
def image(**kwargs):
    print kwargs
    return ""

@msg.subscribe
def subscribe(**kwargs):
	"""
	监听订阅消息
	"""
    print kwargs
    return "欢迎订阅我们的公众号"

@msg.unsubscribe
def unsubscribe(**kwargs):
    print kwargs
    return ""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9900)