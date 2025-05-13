import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

# Rich for UI
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from rich.live import Live
from rich.spinner import Spinner
from rich.layout import Layout

# LangChain components - 使用更新的导入路径
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool, Tool
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.runnables import RunnablePassthrough
from langchain_core.utils.function_calling import convert_to_openai_tool

# LangGraph for memory persistence
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

# 混合模式：LLM和天气使用真实API，地图使用模拟
USE_MOCK_WEATHER = os.getenv("USE_MOCK_WEATHER", "false").lower() == "true"
USE_MOCK_MAP = os.getenv("USE_MOCK_MAP", "true").lower() == "true"

# 根据设置导入相应的函数
if USE_MOCK_MAP:
    # 导入模拟地图函数
    from functionCallListMock import (
        get_coordinates_from_address,
        get_walking_route_planning,
        get_public_transportation_route_planning,
        get_drive_route_planning,
        get_bicycling_route_planning
    )

if USE_MOCK_WEATHER:
    # 导入模拟天气函数
    from functionCallListMock import get_weather
else:
    # 导入真实天气函数
    from functionCallList import get_weather

# 获取时间函数总是实时的
from functionCallList import get_time

# Initialize Rich console
console = Console()

# Load environment variables
load_dotenv()

# Get API credentials
API_KEY = os.getenv("API_KEY", "")  # LLM API key
BASE_URL = os.getenv("BASE_URL", "https://api.siliconflow.cn/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-V3")

# Check if essential API keys are missing
missing_keys = []
if not API_KEY:
    missing_keys.append("API_KEY")

if not USE_MOCK_WEATHER and not os.getenv("WEATHER_API_KEY"):
    missing_keys.append("WEATHER_API_KEY")

if not USE_MOCK_MAP and not os.getenv("AMAP_API_KEY"):
    missing_keys.append("AMAP_API_KEY")

if missing_keys:
    console.print(Panel.fit(
        "[bold red]Missing API Keys[/bold red]\n\n"
        f"The following API keys are missing in your .env file: [yellow]{', '.join(missing_keys)}[/yellow]\n\n"
        "Please follow these steps to set up your environment:\n"
        "1. Copy the .env.example file to .env: [cyan]cp .env.example .env[/cyan]\n"
        "2. Edit the .env file and add your API keys\n"
        "3. Run the application again\n\n"
        f"[bold yellow]Note:[/bold yellow] This application is running in mixed mode:\n"
        f"- Weather API mocking: [{'yellow' if USE_MOCK_WEATHER else 'green'}]{'ENABLED' if USE_MOCK_WEATHER else 'DISABLED'}[/{'yellow' if USE_MOCK_WEATHER else 'green'}]\n"
        f"- Map API mocking: [{'yellow' if USE_MOCK_MAP else 'green'}]{'ENABLED' if USE_MOCK_MAP else 'DISABLED'}[/{'yellow' if USE_MOCK_MAP else 'green'}]\n\n"
        "[bold red]IMPORTANT:[/bold red] Never commit your API keys to version control or share them publicly.",
        title="⚠️ Configuration Warning",
        border_style="red"
    ))
    sys.exit(1)


# Define tool functions using LangChain's tool decorator
@tool
def current_time() -> str:
    """获取当前时间"""
    result = get_time({})
    return result


@tool
def check_weather(location: str) -> str:
    """
    获取指定地点的天气信息
    Args:
        location: 需要查询天气的地点，如杭州、上海、北京等
    """
    result = get_weather({"location": location})
    return result


@tool
def get_coordinates(address: str) -> str:
    """
    将地址转换为经纬度坐标
    Args:
        address: 详细地址，如复旦大学江湾校区、北京天安门等
    """
    result = get_coordinates_from_address({"address": address})
    return result


@tool
def walking_route(source_address: str, destination_address: str) -> str:
    """
    获取步行路线规划
    Args:
        source_address: 起点地址，如复旦大学江湾校区
        destination_address: 终点地址，如五角场
    """
    # 先获取坐标
    source_data = json.loads(get_coordinates_from_address({"address": source_address}))
    destination_data = json.loads(get_coordinates_from_address({"address": destination_address}))
    
    # 检查坐标获取是否成功
    if source_data.get("status") == "1" and source_data.get("geocodes") and \
       destination_data.get("status") == "1" and destination_data.get("geocodes"):
        source = source_data["geocodes"][0]["location"]
        destination = destination_data["geocodes"][0]["location"]
        
        # 获取路线规划
        result = get_walking_route_planning({
            "source": source,
            "destination": destination
        })
        
        return f"步行从{source_address}到{destination_address}的路线：\n{result}"
    else:
        return "无法获取地址坐标，请检查地址是否正确"


@tool
def public_transit_route(source_address: str, destination_address: str, city: str = "上海") -> str:
    """
    获取公共交通路线规划
    Args:
        source_address: 起点地址，如复旦大学江湾校区
        destination_address: 终点地址，如五角场
        city: 城市名称，如上海、北京等，默认为上海
    """
    # 先获取坐标
    source_data = json.loads(get_coordinates_from_address({"address": source_address}))
    destination_data = json.loads(get_coordinates_from_address({"address": destination_address}))
    
    # 检查坐标获取是否成功
    if source_data.get("status") == "1" and source_data.get("geocodes") and \
       destination_data.get("status") == "1" and destination_data.get("geocodes"):
        source = source_data["geocodes"][0]["location"]
        destination = destination_data["geocodes"][0]["location"]
        
        # 获取路线规划
        result = get_public_transportation_route_planning({
            "source": source,
            "destination": destination,
            "city": city
        })
        
        return f"公共交通从{source_address}到{destination_address}的路线：\n{result}"
    else:
        return "无法获取地址坐标，请检查地址是否正确"


@tool
def driving_route(source_address: str, destination_address: str) -> str:
    """
    获取驾车路线规划
    Args:
        source_address: 起点地址，如复旦大学江湾校区
        destination_address: 终点地址，如五角场
    """
    # 先获取坐标
    source_data = json.loads(get_coordinates_from_address({"address": source_address}))
    destination_data = json.loads(get_coordinates_from_address({"address": destination_address}))
    
    # 检查坐标获取是否成功
    if source_data.get("status") == "1" and source_data.get("geocodes") and \
       destination_data.get("status") == "1" and destination_data.get("geocodes"):
        source = source_data["geocodes"][0]["location"]
        destination = destination_data["geocodes"][0]["location"]
        
        # 获取路线规划
        result = get_drive_route_planning({
            "source": source,
            "destination": destination
        })
        
        return f"驾车从{source_address}到{destination_address}的路线：\n{result}"
    else:
        return "无法获取地址坐标，请检查地址是否正确"


@tool
def bicycle_route(source_address: str, destination_address: str) -> str:
    """
    获取骑行路线规划
    Args:
        source_address: 起点地址，如复旦大学江湾校区
        destination_address: 终点地址，如五角场
    """
    # 先获取坐标
    source_data = json.loads(get_coordinates_from_address({"address": source_address}))
    destination_data = json.loads(get_coordinates_from_address({"address": destination_address}))
    
    # 检查坐标获取是否成功
    if source_data.get("status") == "1" and source_data.get("geocodes") and \
       destination_data.get("status") == "1" and destination_data.get("geocodes"):
        source = source_data["geocodes"][0]["location"]
        destination = destination_data["geocodes"][0]["location"]
        
        # 获取路线规划
        result = get_bicycling_route_planning({
            "source": source,
            "destination": destination
        })
        
        return f"骑行从{source_address}到{destination_address}的路线：\n{result}"
    else:
        return "无法获取地址坐标，请检查地址是否正确"


def display_welcome():
    """Display a welcome message with instructions."""
    console.print(Panel.fit(
        "[bold cyan]Welcome to the AI Assistant (LangChain Edition)[/bold cyan]\n\n"
        "This intelligent assistant can answer questions about:\n"
        "- [green]Current time[/green] (e.g., 'What time is it now?')\n"
        "- [green]Weather information[/green] (e.g., 'How's the weather in Shanghai today?')\n"
        "- [green]Route planning[/green] (e.g., 'How do I get from Fudan University to Wujiaochang?')\n\n"
        f"[bold]API Mode:[/bold]\n"
        f"- Weather API: [{'yellow' if USE_MOCK_WEATHER else 'green'}]{'MOCK' if USE_MOCK_WEATHER else 'REAL'}[/{'yellow' if USE_MOCK_WEATHER else 'green'}]\n"
        f"- Map API: [{'yellow' if USE_MOCK_MAP else 'green'}]{'MOCK' if USE_MOCK_MAP else 'REAL'}[/{'yellow' if USE_MOCK_MAP else 'green'}]\n\n"
        "Type [bold yellow]exit[/bold yellow], [bold yellow]quit[/bold yellow], or [bold yellow]bye[/bold yellow] to end the conversation.",
        title="🤖 AI Assistant",
        subtitle="Powered by LangChain & DeepSeek AI",
        border_style="cyan"
    ))


def process_stream_with_ui(content: str):
    """Display streaming content with a nice UI."""
    console.print(Panel(content, title="[bold yellow]A[/bold yellow]: 🤖 Response", border_style="green"))


def main():
    # Display welcome message
    display_welcome()
    
    # Show available capabilities
    capabilities = Table(title="Available Capabilities", box=box.ROUNDED)
    capabilities.add_column("Category", style="cyan")
    capabilities.add_column("Examples", style="green")
    
    capabilities.add_row("Time", "What time is it now?")
    capabilities.add_row("Weather", "How's the weather in Shanghai?\nWhat's the weather forecast for Beijing?")
    capabilities.add_row("Route Planning", "How do I get from Fudan University to Wujiaochang?\nWhat's the best way to travel from Shanghai to Beijing?")
    
    console.print(capabilities)
    
    # Define the tools
    tools = [
        current_time,
        check_weather,
        get_coordinates,
        walking_route,
        public_transit_route,
        driving_route,
        bicycle_route
    ]
    
    # 转换工具格式为OpenAI工具格式
    openai_tools = [convert_to_openai_tool(t) for t in tools]
    
    # 创建系统提示
    system_prompt = """你是一个用于对话场景的智能助手，请正确、简洁、比较口语化地回答问题。
在回答中，你可以使用提供的工具来获取实时信息，如时间、天气和路线规划等。
确保你的回答清晰和有用。
"""
    
    # 创建LLM
    model = ChatOpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
        model=MODEL_NAME,
        streaming=True,
        temperature=0.7
    )
    
    # 直接使用AgentExecutor并处理每次请求，而不使用LangGraph
    # 创建代理
    system_message = SystemMessage(content=system_prompt)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # 对话历史记录
    chat_history = []
    
    # 对话计数
    conversation_count = 0
    
    while True:
        # 添加对话分隔符
        if conversation_count > 0:
            console.rule("[bold blue]New Query[/bold blue]")
        
        # 获取用户输入
        user_input = Prompt.ask("\n[bold yellow]Q[/bold yellow]")
        
        # 退出条件
        if user_input.lower() in ["exit", "quit", "bye"]:
            console.print("[bold cyan]Thank you for using the AI Assistant. Goodbye![/bold cyan]")
            break
        
        # 创建旋转动画
        spinner = Spinner("dots", text="[bold green]Processing your request...[/bold green]")
        
        try:
            # 创建布局，旋转动画在处理时会显示
            layout = Layout()
            layout.update(spinner)
            
            # 使用Live显示旋转动画
            with Live(layout, refresh_per_second=10, console=console) as live:
                # 创建代理
                agent = create_openai_tools_agent(model, tools, prompt)
                agent_executor = AgentExecutor.from_agent_and_tools(
                    agent=agent,
                    tools=tools,
                    verbose=False,
                    return_intermediate_steps=True,
                    handle_parsing_errors=True
                )
                
                # 执行代理
                result = agent_executor.invoke({
                    "input": user_input,
                    "chat_history": chat_history
                })
                
                # 获取结果
                response = result["output"]
            
            # 更新对话历史
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=response))
            
            # 显示结果
            process_stream_with_ui(response)
            
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
            error_message = f"I encountered an error while processing your request. Please try again or rephrase your question."
            process_stream_with_ui(error_message)
        
        conversation_count += 1


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("[bold red]\nProgram interrupted by user. Exiting...[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]") 