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
def worker(name, queue, logger):
    while True:
        # Get a "work item" out of the queue.
        question, access_token, openid =  queue.get()
        # Process task
        openai_to_wechat(question=question, access_token=access_token, openid=openid, logger=logger)
        logger.info(f"Question{question} openid{openid} processed by {name}")
