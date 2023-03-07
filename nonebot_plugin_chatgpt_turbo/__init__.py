import nonebot
import os
import asyncio

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (Message, MessageSegment)
from nonebot.adapters.onebot.v11 import MessageEvent
# from aiohttp import ClientSession
from .ChatSession import ChatSession

try:
    api_key = nonebot.get_driver().config.openai_api_key
    model_id = nonebot.get_driver().config.openai_model_name
except:
    api_key = ""
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


session = {}

chat_request = on_command("", rule=to_me(), block=True, priority=1)


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


clear_request = on_command("/clear", block=True, priority=1)

@clear_request.handle()
async def _(event: MessageEvent):
    del session[event.get_session_id()]
    await clear_request.finish(MessageSegment.text("成功清除历史记录！"), at_sender=True)