# 智能对话系统

这是一个基于大语言模型的智能对话系统，可以回答时间相关问题、天气查询和出行路线规划。

## 功能特点

- 多轮对话：能够理解上下文，进行连续的对话
- 流式响应：回答以流式方式输出，提供更好的用户体验
- 美观的终端界面：使用 Rich 库提供彩色、格式化的终端输出
- 工具调用：支持以下功能
  - 时间查询（如"现在几点了"）
  - 天气查询（如"杭州今天天气如何"）
  - 出行路线规划（如"从复旦大学江湾校区到五角场要怎么走"）

## 安装依赖

使用 requirements.txt 安装所有依赖（推荐）：

```bash
pip install -r requirements.txt
```

或者手动安装各个依赖：

```bash
pip install openai python-dotenv requests rich
```

## 配置

1. 复制 `.env.example` 文件，创建 `.env` 文件

```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填写相关 API 密钥:

```
# DeepSeek API 凭证
API_KEY=your_deepseek_api_key_here
BASE_URL=https://api.siliconflow.cn/v1

# 模型配置
MODEL_NAME=deepseek-ai/DeepSeek-V3

# Weather API 凭证（获取天气信息）
WEATHER_API_KEY=your_weatherapi_key_here  # 从 weatherapi.com 获取

# 高德地图 API 凭证（用于路线规划）
AMAP_API_KEY=your_amap_api_key_here  # 从高德开放平台获取
```

### API 密钥安全

**⚠️ 重要提示**：请妥善保管你的 API 密钥

- **永远不要**将 API 密钥提交到版本控制系统（如 Git）
- **不要**在公开场合分享你的 API 密钥
- 项目中的 `.env` 文件已通过 `.gitignore` 配置排除在版本控制之外
- 如果你不小心泄露了 API 密钥，请立即到相应平台重置或撤销它们

### 获取 API 密钥

- **Weather API**: 访问 [weatherapi.com](https://www.weatherapi.com/)，注册并获取 API 密钥
- **高德地图 API**: 访问[高德开放平台](https://lbs.amap.com/)，注册并创建应用以获取 Web 服务 API 密钥

## 运行

```bash
python run.py
```

## 使用示例

```
Q: 现在几点了？
A: 现在是 2024-05-13 15:30:45

Q: 杭州今天天气怎么样？
A: 杭州今天天气晴朗，气温在22-28°C之间，适宜户外活动。

Q: 从复旦大学江湾校区到五角场怎么走？
A: 您可以选择以下几种方式从复旦大学江湾校区到五角场：
1. 步行：大约需要20分钟，全程1.5公里
2. 公共交通：乘坐地铁10号线，约10分钟可到达
3. 驾车：距离约2公里，正常路况下需要8分钟
4. 骑行：全程约1.5公里，大约需要12分钟
```

## 终端界面预览

程序运行后，会呈现一个美观的终端界面，包括：

- 欢迎信息和使用说明
- 功能表格，展示系统支持的查询类型和示例
- 彩色输出的问答对话
- 实时动画展示 AI 思考和回答过程
- 当调用外部函数时，显示详细的执行信息

使用彩色提示符输入问题，输入 `exit`、`quit` 或 `bye` 结束对话。 