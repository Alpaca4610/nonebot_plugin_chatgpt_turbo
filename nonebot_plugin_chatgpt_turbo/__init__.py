import base64
import httpx
import nonebot

from nonebot import on_command,require
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageSegment,
    PrivateMessageEvent,
    MessageEvent,
    helpers,
    Bot
)

require("nonebot_plugin_saa")
from nonebot_plugin_saa import Text, MessageFactory, AggregatedMessageFactory

from nonebot.plugin import PluginMetadata
from .config import Config, ConfigError
from openai import AsyncOpenAI

__plugin_meta__ = PluginMetadata(
    name="支持OneAPI、DeepSeek、OpenAI聊天Bot",
    description="具有上下文关联和多模态识别（OpenAI），适配OneAPI、硅基流动，DeepSeek官方，OpenAI官方的nonebot插件。",
    usage="""
    @机器人发送问题时机器人不具有上下文回复的能力
    chat 使用该命令进行问答时，机器人具有上下文回复的能力
    lear 清除当前用户的聊天记录
    """,
    config=Config,
    extra={},
    type="application",
    homepage="https://github.com/Alpaca4610/nonebot_plugin_chatgpt_turbo",
    supported_adapters={"~onebot.v11"},
)


plugin_config = Config.parse_obj(nonebot.get_driver().config.dict())

if not plugin_config.oneapi_key:
    raise ConfigError("请配置大模型使用的KEY")
if plugin_config.oneapi_url:
    client = AsyncOpenAI(
        api_key=plugin_config.oneapi_key, base_url=plugin_config.oneapi_url
    )
else:
    client = AsyncOpenAI(api_key=plugin_config.oneapi_key)

model_id = plugin_config.oneapi_model

# public = plugin_config.chatgpt_turbo_public
session = {}

# 带上下文的聊天
chat_record = on_command("chat", block=False, priority=1)

# 不带上下文的聊天
chat_request = on_command("", rule=to_me(), block=False, priority=99)

# 清除历史记录
clear_request = on_command("clear", block=True, priority=1)


# 带记忆的聊天
@chat_record.handle()
async def _(bot: Bot, event: MessageEvent, msg: Message = CommandArg()):
    # 若未开启私聊模式则检测到私聊就结束
    if isinstance(event, PrivateMessageEvent) and not plugin_config.enable_private_chat:
        await Text("对不起，私聊暂不支持此功能。").finish()
    content = msg.extract_plain_text()
    img_url = helpers.extract_image_urls(event.message)
    if content == "" or content is None:
        await Text("内容不能为空！").finish(at_sender=True, reply=True)
    await Text(f"{model_id}正在思考中......").send(at_sender=True, reply=True)

    session_id = event.get_session_id()
    if session_id not in session:
        session[session_id] = []

    if not img_url:
        try:
            session[session_id].append({"role": "user", "content": content})
            response = await client.chat.completions.create(
                model=model_id,
                messages=session[session_id],
            )
        except Exception as error:
            await Text("报错：" + str(error)).finish(at_sender=True, reply=True)

        session[session_id].append(
            {"role": "assistant", "content": response.choices[0].message.content})

        mf2 = MessageFactory([Text(f"{model_id}回复\n" + str(response.choices[0].message.content))])
        
        if hasattr(response.choices[0].message, 'reasoning_content') and plugin_config.r1_reason:
            reasoning_content = response.choices[0].message.reasoning_content
            mf1 = MessageFactory([Text(f"{model_id}思维链\n" + str(reasoning_content))])
            amf = AggregatedMessageFactory([mf1, mf2])
            await amf.finish()
        else:
            if plugin_config.merge_msg:
                await AggregatedMessageFactory([mf2]).finish()
            else:
                await Text(f"{model_id}回复\n" + str(response.choices[0].message.content)).finish(at_sender=True, reply=True)
    else:
        try:
            image_data = base64.b64encode(
                httpx.get(img_url[0]).content).decode("utf-8")
            session[session_id].append(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": content},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_data}"},
                        },
                    ],
                }
            )
            response = await client.chat.completions.create(
                model=model_id, messages=session[session_id]
            )
        except Exception as error:
            await Text("报错："+str(error)+"，很可能因为该模型不支持多模态").finish(at_sender=True, reply=True)
        session[session_id].append(
            {"role": "assistant", "content": response.choices[0].message.content})
        if plugin_config.merge_msg:
                AggregatedMessageFactory([mf2]).finish()
        else:
            await Text(f"{model_id}回复\n" + str(response.choices[0].message.content)).finish(at_sender=True, reply=True)


# 不带记忆的对话
@chat_request.handle()
async def _(bot: Bot, event: MessageEvent, msg: Message = CommandArg()):
    if isinstance(event, PrivateMessageEvent) and not plugin_config.enable_private_chat:
        await Text("对不起，私聊暂不支持此功能。").finish()
    content = msg.extract_plain_text()
    img_url = helpers.extract_image_urls(event.message)
    if content == "" or content is None:
        await Text("内容不能为空！").finish(at_sender=True, reply=True)
    await Text(f"{model_id}正在思考中......").send(at_sender=True, reply=True)

    if not img_url:
        try:
            response = await client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": content}],
            )
        except Exception as error:
            await Text("报错：" + str(error)).finish(at_sender=True, reply=True)

        mf2 = MessageFactory([Text(f"{model_id}回复\n" + str(response.choices[0].message.content))])
        
        if hasattr(response.choices[0].message, 'reasoning_content') and plugin_config.r1_reason:
            reasoning_content = response.choices[0].message.reasoning_content
            mf1 = MessageFactory([Text(f"{model_id}思维链\n" + str(reasoning_content))])
            amf = AggregatedMessageFactory([mf1, mf2])
            await amf.finish()
        else:
            if plugin_config.merge_msg:
                await AggregatedMessageFactory([mf2]).finish()
            else:
                await Text(f"{model_id}回复\n" + str(response.choices[0].message.content)).finish(at_sender=True, reply=True)
    else:
        try:
            image_data = base64.b64encode(
                httpx.get(img_url[0]).content).decode("utf-8")
            response = await client.chat.completions.create(
                model=model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": content},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                },
                            },
                        ],
                    }
                ],
            )
        except Exception as error:
            await Text("报错："+str(error)+"，很可能因为该模型不支持多模态").finish(at_sender=True, reply=True)
        if plugin_config.merge_msg:
                AggregatedMessageFactory([mf2]).finish()
        else:
            await Text(f"{model_id}回复\n" + str(response.choices[0].message.content)).finish(at_sender=True, reply=True)


@clear_request.handle()
async def _(event: MessageEvent):
    del session[event.get_session_id()]
    await clear_request.finish(
        MessageSegment.text("成功清除历史记录！"), at_sender=True
    )


# # 根据消息类型创建会话id
# def create_session_id(event):
#     if isinstance(event, PrivateMessageEvent):
#         session_id = f"Private_{event.user_id}"
#     elif public:
#         session_id = event.get_session_id().replace(f"{event.user_id}", "Public")
#     else:
#         session_id = event.get_session_id()
#     return session_id
