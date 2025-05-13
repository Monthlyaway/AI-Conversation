import json
from openai import OpenAI

from functionCallRegistry import function_registry, function_desc


BASE_URL = "YOUR LLM URL"
API_KEY = "YOUR API KEY"


client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

messages = [
    {"role": "system", "content": "你是一个用于对话场景的智能助手，请正确、简洁、比较口语化地回答问题。你能够使用提供的tools（函数）来回答问题，有必要时需要从用户提问中抽取函数所需要的参数"},
    {"role": "user", "content": "现在几点了？"}
]

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=function_desc)

message = response.choices[0].message
messages.append(
    {"role": "assistant", "tool_calls": message.tool_calls, "content": None})

tool = message.tool_calls[0]
function_name = tool.function.name
function_arguments = json.loads(tool.function.arguments)
function_result = function_registry.get(function_name)(function_arguments)
messages.append({"role": "tool", "tool_call_id": tool.id,
                "content": function_result})

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=function_desc)

print(response.choices[0].message.content)
