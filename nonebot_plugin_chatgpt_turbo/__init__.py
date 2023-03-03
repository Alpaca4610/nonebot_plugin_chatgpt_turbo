import openai
import nonebot
import asyncio

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (Message, MessageSegment)
from nonebot.adapters.onebot.v11 import MessageEvent
from aiohttp import ClientSession

try:
    api_key = nonebot.get_driver().config.openai_api_key
    model_id = nonebot.get_driver().config.openai_model_name
except:
    api_key = ""
    model_id = "gpt-3.5-turbo"


def get_response(user_id, content):
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


chat_request = on_command("", rule=to_me(), block=True, priority=1)

@chat_request.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    if api_key == "":
        await chat_request.finish(MessageSegment.text("请先配置openai_api_key"))

    content = msg.extract_plain_text()
    if content == "" or content is None:
        await chat_request.finish(MessageSegment.text("内容不能为空！"))

    await chat_request.send(MessageSegment.text("ChatGPT正在思考中......"))

    loop =  asyncio.get_event_loop()
    try:
        openai.aiosession.set(ClientSession())
        res = await loop.run_in_executor(None, get_response, event.user_id, content)
        await openai.aiosession.get().close()

    except Exception as error:
        await chat_request.finish(str(error))
    await chat_request.finish(MessageSegment.text(res))
