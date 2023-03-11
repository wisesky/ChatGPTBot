#! python3
# -*- encoding: utf-8 -*-
'''
@File   : chatGPT.py
@Time   : 2023/03/06 12:09:45
@Author : Franklin Chen
@Contact: wisesky1988@gmail.com
@Licence: MIT License
@Desc   : 
'''

import os
import openai
import requests
import json

#TODO 如何保存上下文聊天
def get_answer_from_openai(question, openai_api_key,logger):
    openai.api_key = openai_api_key
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            # {"role": "system", "content": "You are a helpful assistant."},
            # {"role": "user", "content": "Who won the world series in 2020?"},
            # {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            # {"role": "user", "content": "Where was it played?"},
            {"role": "user", "content": question},
        ]        
    )
    logger.info(f"Send Question : {question}  \n Get answer from openai : {response}")
    """
    response format
            {
        'id': 'chatcmpl-6p9XYPYSTTRi0xEviKjjilqrWU2Ve',
        'object': 'chat.completion',
        'created': 1677649420,
        'model': 'gpt-3.5-turbo',
        'usage': {'prompt_tokens': 56, 'completion_tokens': 31, 'total_tokens': 87},
        'choices': [
        {
            'message': {
            'role': 'assistant',
            'content': 'The 2020 World Series was played in Arlington, Texas at the Globe Life Field, which was the new home stadium for the Texas Rangers.'},
            'finish_reason': 'stop',
            'index': 0
        }
        ]
        }
    """
    return response['choices'][0]['message']['content']

def answer_to_wechat(answer:str, access_token, openid, logger):
    """
        假如服务器无法保证在五秒内处理并回复，必须做出下述回复，这样微信服务器才不会对此作任何处理，并且不会发起重试
        （这种情况下，可以使用客服消息接口进行异步回复）
    下面是异步回复的接口:
    微信公众平台  
        ->  客服接口 :  POST https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=ACCESS_TOKEN
                -> 发消息
            JSON 数据包
        {
        "touser":"OPENID",
        "msgtype":"text",
        "text":
        {
            "content":"Hello World"
        }
    }

    """
    # 预处理answer ，去掉开头的回车符\n
    post_answer = answer
    while post_answer.startswith('\n') :
        post_answer = post_answer[1: ]
    url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
    data = {
        "touser":openid,
        "msgtype":"text",
        "text":
        {
            "content":post_answer
        }
    }
    # 微信发送消息，客服消息接口，必须是json，不能是data
    # 同时为了包装json内部的英文编码，需要用非ascii，用unicode编码
    json_data = json.dumps(data, ensure_ascii=False)
    r = requests.post(url, data=json_data.encode('utf8'))
    logger.info(f"send answer : {answer} \n Get response from wechat server  : {r.text}")
    return 

def openai_to_wechat(question, access_token, openid, openai_api_key,logger):
    """
    一轮完整的问答请求
    """
    answer = get_answer_from_openai(question=question, openai_api_key=openai_api_key, logger=logger)
    answer_to_wechat(answer=answer, access_token=access_token, openid=openid, logger=logger)
    # 保存聊天记录
    print(f"User({openid} : {question} \nChatBot : {answer} ", file=open(f"./log/{openid}.log", mode="at"))
    return
