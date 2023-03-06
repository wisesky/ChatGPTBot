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
from weixin import Weixin, WeixinError, WeixinMsg
from multiprocessing import Process, Queue
from logger import create_logger
from eliot import to_file, log_call

from queue_multiprocess import worker


logger = create_logger('./log', name='chatgpt')
to_file(open('./log/eliot.log', 'w'))

app = Flask(__name__)
app.debug = True

q = Queue(1000)

# 具体导入配
# 根据需求导入仅供参考
# app.config.from_object(dict(WEIXIN_APP_ID='wx3a9d69fe1255c373', WEIXIN_APP_SECRET='eaa2205021de096728fe01a44755b073', WEIXIN_TOKEN='7c0cd95f55c61fe37e8ed9e27171c2ec'))
app.config["WEIXIN_APP_ID"] = 'wx3a9d69fe1255c373'
app.config['WEIXIN_APP_SECRET'] = 'eaa2205021de096728fe01a44755b073'
app.config['WEIXIN_TOKEN']='7c0cd95f55c61fe37e8ed9e27171c2ec'

# 初始化
wx = Weixin()
wx.init_app(app)

# 微信消息
# msg = WeixinMsg("7c0cd95f55c61fe37e8ed9e27171c2ec")
# TODO: check wx.msg property
msg = wx.msg 


app.add_url_rule("/", view_func=msg.view_func)

@msg.all
def all_test(**kwargs):
    logger.info(kwargs)
    # 或者直接返回
    # return "all"
    return msg.reply(
        kwargs['sender'], sender=kwargs['receiver'], content='all'
    )

# @log_call
@msg.text()
def hello(**kwargs):
    logger.info(str(kwargs))
    question = kwargs.get("content", "Who are you?")
    access_token = wx.mp.access_token
    openid = kwargs['sender']
    q.put((question,access_token, openid)) # question, access_token, openid
    return msg.reply(
        kwargs['sender'], sender=kwargs['receiver'], content=''
    ) # 5s 不回复 'success' or '' ，会回复公众号故障, 提前回复避免提示
    # try:
    #     reply = get_reply(kwargs.get('content','你是谁'), logger)
    #     return dict(content=str(reply), type="text")
    # except Exception as e:
    #     logger.error(str(e))
    #     return dict(content="AI机器人正在紧急修复中，请过会儿再试", type="text")


@msg.text("world")
def world(**kwargs):
    return msg.reply(
        kwargs['sender'], sender=kwargs['receiver'], content='hello world!'
    )


@msg.image
def image(**kwargs):
    logger.info(kwargs)
    return ""


@msg.subscribe
def subscribe(**kwargs):
    logger.info(kwargs)
    return ""


@msg.unsubscribe
def unsubscribe(**kwargs):
    logger.info(kwargs)
    return ""


if __name__ == '__main__':
    consumer = Process(target=worker , args=("Work_1", q, logger))
    consumer.daemon = True
    consumer.start()

    app.run(host="0.0.0.0", port=9900)
