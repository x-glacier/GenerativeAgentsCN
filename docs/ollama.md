# 安装

下载地址：https://ollama.com/

默认选项安装即可。

# 下载模型

在终端窗口输入命令，下载需要的模型。

例如本项目默认使用的大语言模型是`qwen2.5-7b`，嵌入模型是`bge-m3`，可通过以下命令下载：
```
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama pull bge-m3:latest
```

*注：MacOS系统m1/m2芯片，16G以上内存，建议使用qwen2.5-7b模型。Windows系统30/40系列N卡，12G以上显存，可使用qwen2.5-14b或更大的量化模型*

# 运行

可直接双击Ollama图标启动服务，也可通过命令行启动：
```
ollama serve
```

# 配置

## 开启API

Windows系统启动服务前需要先配置系统环境变量，否则访问API服务报403错误：
```
OLLAMA_HOST=0.0.0.0
OLLAMA_ORIGINS=*
```
配置方法：
右键“我的电脑”->属性->高级系统设置->环境变量->系统变量->新建。
在`变量名`和`变量值`中分别填入`OLLAMA_HOST`和`0.0.0.0`，即完成对`OLLAMA_HOST`环境变量的配置。其余环境变量同理。

MacOS系统通过以下命令设置环境变量：
```
launchctl setenv OLLAMA_HOST "0.0.0.0"
launchctl setenv OLLAMA_ORIGINS "*"
```

*启动后默认监听端口：11434*

# 常用设置

## 1. 解决外网访问的问题
```
OLLAMA_HOST=0.0.0.0
```

## 2. 解决Windows系统默认将模型下载到C盘的问题
```
OLLAMA_MODELS=E:\OllamaModels
```

## 3. 设置模型加载到内存中保留2小时
*默认情况下，模型在卸载之前会在内存中保留 5 分钟*
```
OLLAMA_KEEP_ALIVE=2h
```

## 4. 修改默认端口
```
OLLAMA_HOST=0.0.0.0:8000
```

## 5. 设置多个用户并发请求
```
OLLAMA_NUM_PARALLEL=2
```

## 6. 设置同时加载多个模型
```
OLLAMA_MAX_LOADED_MODELS=2
```
