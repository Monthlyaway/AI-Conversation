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

# LangChain components
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.tools import tool, StructuredTool
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory

# Using mock data for testing without API keys
from functionCallListMock import (
    get_time, 
    get_weather, 
    get_coordinates_from_address,
    get_walking_route_planning,
    get_public_transportation_route_planning,
    get_drive_route_planning,
    get_bicycling_route_planning
)

# Initialize Rich console
console = Console()

# Load environment variables
load_dotenv()

# Get API credentials
API_KEY = os.getenv("API_KEY", "")  # LLM API key
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-V3")  # Use specified model
USE_MOCK_DATA = True  # 默认使用模拟数据进行测试

# Check if essential API keys are missing
if not API_KEY:
    console.print(Panel.fit(
        "[bold red]Missing API Key[/bold red]\n\n"
        "LLM API key is missing in your .env file.\n\n"
        "Please follow these steps to set up your environment:\n"
        "1. Copy the .env.example file to .env: [cyan]cp .env.example .env[/cyan]\n"
        "2. Edit the .env file and add your API key\n"
        "3. Run the application again\n\n"
        "[bold yellow]Note:[/bold yellow] This application is running in mock mode, which means it can operate without "
        "Weather and Amap API keys by using simulated data.\n\n"
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
        f"[bold {'yellow' if USE_MOCK_DATA else 'green'}]{'MOCK MODE ACTIVE' if USE_MOCK_DATA else 'USING REAL APIs'}[/bold {'yellow' if USE_MOCK_DATA else 'green'}]\n\n"
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
    
    # Create system prompt for the agent
    system_prompt = """你是一个用于对话场景的智能助手，请正确、简洁、比较口语化地回答问题。
在回答中，你可以使用提供的工具来获取实时信息，如时间、天气和路线规划等。
确保你的回答清晰和有用。
"""
    
    # Set up the language model
    model = ChatOpenAI(
        openai_api_key=API_KEY,
        openai_api_base=os.getenv("BASE_URL"),
        model=MODEL_NAME,
        streaming=True,
        temperature=0.7
    )
    
    # Create a memory buffer to maintain conversation context
    memory = ConversationBufferMemory(return_messages=True)
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    
    # Create the agent
    agent = create_structured_chat_agent(
        llm=model,
        tools=tools,
        prompt=prompt
    )
    
    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=False,
        return_intermediate_steps=False
    )
    
    # Conversation loop
    conversation_count = 0
    while True:
        # Add a separator between conversations
        if conversation_count > 0:
            console.rule("[bold blue]New Query[/bold blue]")
        
        # Get user input with a stylish prompt
        user_input = Prompt.ask("\n[bold yellow]Q[/bold yellow]")
        
        # Exit condition
        if user_input.lower() in ["exit", "quit", "bye"]:
            console.print("[bold cyan]Thank you for using the AI Assistant. Goodbye![/bold cyan]")
            break
        
        # Process user input with LangChain agent
        console.print("[bold green]Processing your request...[/bold green]")
        
        try:
            # The streaming callback approach
            result = ""
            
            response_panel = Panel("", title="[bold yellow]A[/bold yellow]: 🤖 Response", border_style="green")
            
            # Live display to show streaming output
            with Live(response_panel, refresh_per_second=10, console=console) as live:
                for chunk in agent_executor.stream({"input": user_input}):
                    if chunk.get("chunks"):
                        for token in chunk["chunks"]:
                            if isinstance(token, str):
                                result += token
                                # Update the panel with each new token
                                response_panel = Panel(
                                    result, 
                                    title="[bold yellow]A[/bold yellow]: 🤖 Response", 
                                    border_style="green"
                                )
                                live.update(response_panel)
        
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
            result = f"I encountered an error while processing your request. Please try again or rephrase your question."
            process_stream_with_ui(result)
        
        conversation_count += 1


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("[bold red]\nProgram interrupted by user. Exiting...[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]") 