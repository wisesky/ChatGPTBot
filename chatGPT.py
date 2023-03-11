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

def process_answer_for_wechat(answer):
    """
    预处理answer， 返回列表形式的answer
    """
    # 去掉开头的回车符\n
    post_answer = answer
    while post_answer.startswith('\n') :
        post_answer = post_answer[1: ]
    # 切分符合微信字数要求的消息 : 600字
    answers = [answer[pos:pos+600] for pos in range(0,len(answer), 600)]
    return answers

def reply_to_wechat(answer:str, access_token, openid, logger):
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
    url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
    data = {
        "touser":openid,
        "msgtype":"text",
        "text":
        {
            "content":answer
        }
    }
    # 微信发送消息，客服消息接口，必须是json，
    # 由于 requests 参数 data会根据数据类型判断选择是否用json发送，
    # 然而 直接用json参数，会触发自动的dict->json格式转换,默认转换方式不支持中文，
    # 所以包装json内部的非英文编码，需要用非ascii，用unicode编码， 同时用utf8编码
    json_data = json.dumps(data, ensure_ascii=False)
    r = requests.post(url, data=json_data.encode('utf8'))
    try:
        r_json = r.json()
        if r_json['errcode'] == 0 and r_json['errmsg'] is 'ok':
            # {"errcode":0,"errmsg":"ok"}
            logger.info(f"Answer Send Successfully ,answer : {answer} ")
        else:
            logger.error(f"Answer Send Failed, answer : {answer} \nerror text : {r.text}")
    except Exception as e:
        logger.error(f"客服消息接口发送失败 ,status_code : {r.status_code} , \nException : {str(e)}")
    return 

def answer_to_wechat(answer:str, access_token, openid, logger):
    """
    预处理回答answer
    逐条发送answer
    """    
    answers = process_answer_for_wechat(answer)
    for answer in answers:
        reply_to_wechat(answer=answer,access_token=access_token, openid=openid, logger=logger)
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
