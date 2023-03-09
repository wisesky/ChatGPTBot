#! python3
# -*- encoding: utf-8 -*-
'''
@File   : queue_multiprocess.py
@Time   : 2023/03/07 02:46:59
@Author : Franklin Chen
@Contact: wisesky1988@gmail.com
@Licence: MIT License
@Desc   : 
'''


import asyncio
import random
import time
import requests
from eliot import log_call

from chatGPT import openai_to_wechat

# @log_call
#TODO 多进程下，并发日志写问题
def worker(name, queue, openai_api_key ,logger):
    while True:
        # Get a "work item" out of the queue.
        question, access_token, openid =  queue.get()
        # Process task
        openai_to_wechat(question=question, access_token=access_token, openid=openid, openai_api_key=openai_api_key,logger=logger)
        logger.info(f"\nQuestion: {question} \nopenid: {openid}  \nprocessed by {name}")
