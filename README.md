<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-chatgpt-turbo
</div>

# 介绍
- 本插件适配OneAPI和OpenAI接口，可以在nonebot中调用OpenAI官方或是OneAPI(gpt系列模型,gemini-1.5-pro)接口的模型进行回复。
- 本插件具有上下文回复和多模态识别（识图）功能。
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
oneapi_key = ""  # OpenAI官方或者是支持OneAPI的大模型中转服务商提供的KEY
oneapi_model = "gpt-4o" # 使用的语言大模型，使用识图功能请填写合适的大模型名称
```

可选内容：
```
oneapi_url = ""  # （可选）大模型中转服务商提供的中转地址，使用OpenAI官方服务不需要填写
enable_private_chat = True   # 私聊开关，默认开启，改为False关闭
```

# 效果
![](demo.jpg)

# 使用方法

- @机器人发送问题时机器人不具有上下文回复的能力
- chat 使用该命令进行问答时，机器人具有上下文回复的能力
- clear 清除当前用户的聊天记录
