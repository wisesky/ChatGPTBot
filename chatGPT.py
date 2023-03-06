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

def get_reply(content, logger):
    logger.info("get_reply : Start  ****************")
    openai.api_key = os.getenv("OPENAI_API_KEY")
    logger.info("Send content >>>")
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            # {"role": "system", "content": "You are a helpful assistant."},
            # {"role": "user", "content": "Who won the world series in 2020?"},
            # {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            # {"role": "user", "content": "Where was it played?"},
            {"role": "user", "content": content},
        ]        
    )
    logger.info("Get response from openai")
    logger.info("get_reply : End  ****************")
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

