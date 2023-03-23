import nonebot
import openai

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from .config import Config, ConfigError
from .ChatSession import ChatSession

plugin_config = Config.parse_obj(nonebot.get_driver().config.dict())

if plugin_config.openai_http_proxy:
    proxy = {'http': plugin_config.openai_http_proxy, 'https': plugin_config.openai_http_proxy}
else:
    proxy = ""

if not plugin_config.openai_api_key:
    raise ConfigError("请设置 openai_api_key")

api_key = plugin_config.openai_api_key
model_id = plugin_config.openai_model_name
max_limit = plugin_config.openai_max_history_limit
session = {}

# 带上下文的聊天
chat_request = on_command("chat", block=True, priority=1)


@chat_request.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if api_key == "":
        await chat_request.finish(MessageSegment.text("请先配置openai_api_key"), at_sender=True)

    content = msg.extract_plain_text()
    if content == "" or content is None:
        await chat_request.finish(MessageSegment.text("内容不能为空！"), at_sender=True)

    await chat_request.send(MessageSegment.text("ChatGPT正在思考中......"))

    if event.get_session_id() not in session:
        session[event.get_session_id()] = ChatSession(api_key=api_key, model_id=model_id, max_limit=max_limit)

    try:
        res = await session[event.get_session_id()].get_response(content, proxy)

    except Exception as error:
        await chat_request.finish(str(error), at_sender=True)
    await chat_request.finish(MessageSegment.text(res), at_sender=True)


# 不带上下文的聊天
chat_request2 = on_command("", rule=to_me(), block=True, priority=99)


async def get_response(content, proxy):
    openai.api_key = api_key
    if proxy != "":
        openai.proxy = proxy

    res_ = await openai.ChatCompletion.acreate(
        model=model_id,
        messages=[
            {"role": "user", "content": content}
        ]
    )

    res = res_.choices[0].message.content

    while res.startswith("\n") != res.startswith("？"):
        res = res[1:]

    return res


@chat_request2.handle()
async def _(msg: Message = CommandArg()):
    content = msg.extract_plain_text()
    if content == "" or content is None:
        await chat_request2.finish(MessageSegment.text("内容不能为空！"))

    await chat_request2.send(MessageSegment.text("ChatGPT正在思考中......"))

    try:
        res = await get_response(content, proxy)

    except Exception as error:
        await chat_request2.finish(str(error))
    await chat_request2.finish(MessageSegment.text(res))


clear_request = on_command("clear", block=True, priority=1)


@clear_request.handle()
async def _(event: GroupMessageEvent):
    del session[event.get_session_id()]
    await clear_request.finish(MessageSegment.text("成功清除历史记录！"), at_sender=True)


if plugin_config.enable_private_chat:
    private_chat_request = on_command("chat", block=True, priority=1)


    @private_chat_request.handle()
    async def _(event: PrivateMessageEvent, msg: PrivateMessageEvent):
        content = msg.extract_plain_text()
        if content == "" or content is None:
            await private_chat_request.finish(MessageSegment.text("内容不能为空！"), at_sender=True)

        await private_chat_request.send(MessageSegment.text("ChatGPT正在思考中......"))

        if event.get_user_id() not in session:
            session[event.get_user_id()] = ChatSession(api_key=api_key, model_id=model_id, max_limit=max_limit)

        try:
            res = await session[event.get_user_id()].get_response(content, proxy)

        except Exception as error:
            await chat_request.finish(str(error), at_sender=True)
        await private_chat_request.finish(MessageSegment.text(res), at_sender=True)


    # 不带上下文的聊天
    private_chat_request2 = on_command("", rule=to_me(), block=True, priority=99)


    @private_chat_request2.handle()
    async def _(msg: PrivateMessageEvent):
        if api_key == "":
            await private_chat_request2.finish(MessageSegment.text("请先配置openai_api_key"))

        content = msg.extract_plain_text()
        if content == "" or content is None:
            await private_chat_request2.finish(MessageSegment.text("内容不能为空！"))

        await private_chat_request2.send(MessageSegment.text("ChatGPT正在思考中......"))

        try:
            res = await get_response(content, proxy)

        except Exception as error:
            await private_chat_request2.finish(str(error))
        await private_chat_request2.finish(MessageSegment.text(res))


    private_clear_request = on_command("/clear", block=True, priority=1)


    @private_clear_request.handle()
    async def _(event: PrivateMessageEvent):
        del session[event.get_user_id()]
        await private_clear_request.finish(MessageSegment.text("成功清除历史记录！"), at_sender=True)
