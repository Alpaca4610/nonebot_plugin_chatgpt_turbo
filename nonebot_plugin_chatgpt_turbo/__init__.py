import nonebot
import os
import asyncio
import openai

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (Message, MessageSegment)
from nonebot.adapters.onebot.v11 import MessageEvent
# from aiohttp import ClientSession
from .ChatSession import ChatSession

try:
    api_key = nonebot.get_driver().config.openai_api_key
except:
    api_key = ""
    
try:
    model_id = nonebot.get_driver().config.openai_model_name
except:
    model_id = "gpt-3.5-turbo"

try:
    max_limit = nonebot.get_driver().config.openai_max_history_limit
except:
    max_limit = 30

try:
    http_proxy = nonebot.get_driver().config.openai_http_proxy
except:
    http_proxy = ""


if http_proxy != "":
    os.environ["http_proxy"] = http_proxy
    os.environ["https_proxy"] = http_proxy
    

session = {}


# 带上下文的聊天
chat_request = on_command("/chat", block=True, priority=1)


@chat_request.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    if api_key == "":
        await chat_request.finish(MessageSegment.text("请先配置openai_api_key"), at_sender=True)

    content = msg.extract_plain_text()
    if content == "" or content is None:
        await chat_request.finish(MessageSegment.text("内容不能为空！"), at_sender=True)

    await chat_request.send(MessageSegment.text("ChatGPT正在思考中......"))

    loop = asyncio.get_event_loop()
    if event.get_session_id() not in session:
        session[event.get_session_id()] = ChatSession(api_key=api_key, model_id=model_id, max_limit=max_limit)

    try:
        # openai.aiosession.set(ClientSession())
        # res = session[event.get_session_id()].get_response(content)
        res = await loop.run_in_executor(None, session[event.get_session_id()].get_response, content)
        # await openai.aiosession.get().close()

    except Exception as error:
        await chat_request.finish(str(error), at_sender=True)
    await chat_request.finish(MessageSegment.text(res), at_sender=True)


# 不带上下文的聊天
chat_request2 = on_command("", rule=to_me(), block=True, priority=1)

def get_response(content):
    openai.api_key = api_key
    res_ = openai.ChatCompletion.create(
        model=model_id,
        messages=[
            {"role": "user", "content": content}
        ]
    )

    res = res_.choices[0].message.content

    while res.startswith("\n") != res.startswith("？"):
        res = res[1:]
    print(res)

    return res

@chat_request2.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    print(event.get_session_id())
    if api_key == "":
        await chat_request2.finish(MessageSegment.text("请先配置openai_api_key"))

    content = msg.extract_plain_text()
    if content == "" or content is None:
        await chat_request2.finish(MessageSegment.text("内容不能为空！"))

    await chat_request2.send(MessageSegment.text("ChatGPT正在思考中......"))

    loop =  asyncio.get_event_loop()
    try:
        res = await loop.run_in_executor(None, get_response, content)

    except Exception as error:
        await chat_request2.finish(str(error))
    await chat_request2.finish(MessageSegment.text(res))


clear_request = on_command("/clear", block=True, priority=1)

@clear_request.handle()
async def _(event: MessageEvent):
    del session[event.get_session_id()]
    await clear_request.finish(MessageSegment.text("成功清除历史记录！"), at_sender=True)