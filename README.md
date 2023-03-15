<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-chatgpt-turbo
</div>

# 介绍
- 本插件适配OpenAI在2023年3月1日发布的最新版API，可以在nonebot中调用OpenAI的ChatGPT生产环境下的模型（GPT3.5-turbo）进行回复。
- 接口调用速度与网络环境有关，经过测试，大陆外的服务器的OpenAI API响应时间能在十秒之内。
- 免费版OpenAI的调用速度限制为20次/min
- 本插件具有上下文回复功能(可选)，根据每个成员与机器人最近30条（可修改）的聊天记录进行响应回复,该功能消耗服务器资源较大
# 安装

* 手动安装
  ```
  git clone https://github.com/Alpaca4610/nonebot_plugin_chatgpt_turbo.git
  ```

  下载完成后在bot项目的pyproject.toml文件手动添加插件：

  ```
  plugin_dirs = ["xxxxxx","xxxxxx",......,"下载完成的插件路径/nonebot-plugin-gpt3.5-turbo"]
  ```
* 使用 pip
  ```
  pip install nonebot-plugin-chatgpt-turbo
  ```

# 配置文件

在Bot根目录下的.env文件中追加如下内容：

```
OPENAI_API_KEY = key
OPENAI_MODEL_NAME = "gpt-3.5-turbo"
OPENAI_HTTP_PROXY = "http://127.0.0.1:8001"    # 请使用代理访问api，中国大陆/香港IP调用API有几率会被封禁
```

可选内容：
```
OPENAI_MAX_HISTORY_LIMIT = 30   # 保留与每个用户的聊天记录条数
ENABLE_PRIVATE_CHAT = True   # 私聊开关，默认开启，改为False关闭
```


# 使用方法

- @机器人发送问题时机器人不具有上下文回复的能力
- chat 使用该命令进行问答时，机器人具有上下文回复的能力
- clear 清除当前用户的聊天记录
