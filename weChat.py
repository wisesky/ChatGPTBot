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
import os
from datetime import datetime, timedelta
from multiprocessing import Process, Queue
from logger import create_logger
from eliot import to_file, log_call
from pathlib import Path

from flask import Flask, jsonify, request, url_for
from weixin import Weixin, WeixinError, WeixinMsg

from queue_multiprocess import worker

APP_IP = "127.0.0.1"
APP_PORT = 9900
# 公众号： 禽兽兄弟 相关开发info
WEIXIN_APP_ID = "wx3a9d69fe1255c373"
WEIXIN_APP_SECRET = "eaa2205021de096728fe01a44755b073"
WEIXIN_TOKEN = "7c0cd95f55c61fe37e8ed9e27171c2ec"
# openai api key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")

log_dir = Path("./log")
quene_length = 1000

def __init__():
    logger = create_logger(log_dir, name='ChatGPTBot')
    to_file(open(log_dir/'eliot.log', 'w'))

    queue = Queue(1000)

    app = Flask(__name__)
    app.debug = True
    # 根据需求导入配置
    app.config["WEIXIN_APP_ID"] = WEIXIN_APP_ID
    app.config['WEIXIN_APP_SECRET'] = WEIXIN_APP_SECRET
    app.config['WEIXIN_TOKEN']= WEIXIN_TOKEN

    # 初始化 weixin-python
    wx = Weixin()
    wx.init_app(app)
    msg = wx.msg 

    app.add_url_rule("/", view_func=msg.view_func)

    return app, wx, queue, logger

def msgHandler(wx: Weixin, queue:Queue):
    """
    微信公众平台被动回复用户消息接口
    回复处理Handler

    WeixinMsg -> view_func 负责处理所有被装饰器包装的接口，根据返回类型不同，会有不同的返回
        1> dict(content="CONTENT", type="text") ，会被添加 ToUserName, FromUserName 包装成xml格式，返回，这是标准返回给微信服务器的格式
                eg: 
                    <xml>
                        <ToUserName><![CDATA[toUser]]></ToUserName>
                        <FromUserName><![CDATA[fromUser]]></FromUserName>
                        <CreateTime>12345678</CreateTime>
                        <MsgType><![CDATA[text]]></MsgType>
                        <Content><![CDATA[你好]]></Content>
                    </xml>
        2> msg.reply(sender, receiver, type, content) 功能同上，实际上，上述代码最终也会调用本接口返回
        3> “字符串内容” ，如果只是单纯的字符串，那么就不会被包装成微信的xml格式，将直接回复字符串内容

    """
    msg = wx
    @msg.all
    def all_test(**kwargs):
        logger.info(kwargs)
        # 或者直接返回
        # return "all"
        return msg.reply(
            kwargs['sender'], sender=kwargs['receiver'], content='all'
        )

    @msg.text()
    def text(**kwargs):
        """
        假如服务器无法保证在五秒内处理并回复，必须做出下述回复，
        1、直接回复success（推荐方式） 2、直接回复空串（指字节长度为0的空字符串，而不是 XML 结构体中 content 字段的内容为空）
        这样微信服务器才不会对此作任何处理，并且不会发起重试
        （这种情况下，可以使用客服消息接口进行异步回复）

        此处直接返回空，这样进入异步回复流程，注意要直接返回空字符串，否则就会被包装成微信标准xml格式，反而给微信公众平台错误的信息
        """
        logger.info(str(kwargs))
        question = kwargs.get("content", "Who are you?")
        access_token = wx.mp.access_token
        openid = kwargs['sender']
        queue.put((question,access_token, openid)) # question, access_token, openid
        # return dict(content='success', type="text")
        return ""
        # 5s 不回复 'success' or '' ，会回复公众号故障, 提前回复避免提示

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

    return msg

if __name__ == '__main__':
    app, wx, queue,logger = __init__()
    msg = msgHandler(wx, queue)

    consumer = Process(target=worker , args=("Work_1", queue, OPENAI_API_KEY, logger))
    consumer.daemon = True
    consumer.start()

    app.run(host=APP_IP, port=APP_PORT)
