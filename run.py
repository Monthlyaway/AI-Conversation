import json
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich import box

from functionCallRegistry import function_registry, function_desc

# Initialize Rich console
console = Console()

# Load environment variables from .env file
load_dotenv()

# Get API credentials and model configuration from environment variables
API_KEY = os.getenv("API_KEY", "")  # No default key for security
BASE_URL = os.getenv("BASE_URL", "https://api.siliconflow.cn/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-V3")

# Check if API keys are set
missing_keys = []
if not API_KEY:
    missing_keys.append("API_KEY")
if not os.getenv("WEATHER_API_KEY"):
    missing_keys.append("WEATHER_API_KEY")
if not os.getenv("AMAP_API_KEY"):
    missing_keys.append("AMAP_API_KEY")

if missing_keys:
    console.print(Panel.fit(
        "[bold red]Missing API Keys[/bold red]\n\n"
        f"The following API keys are missing in your .env file: [yellow]{', '.join(missing_keys)}[/yellow]\n\n"
        "Please follow these steps to set up your environment:\n"
        "1. Copy the .env.example file to .env: [cyan]cp .env.example .env[/cyan]\n"
        "2. Edit the .env file and add your API keys\n"
        "3. Run the application again\n\n"
        "[bold red]IMPORTANT:[/bold red] Never commit your API keys to version control or share them publicly. "
        "The .env file is listed in .gitignore to help keep your keys secure.",
        title="⚠️ Configuration Error",
        border_style="red"
    ))
    sys.exit(1)

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# Initialize messages with system message
messages = [
    {"role": "system", "content": "你是一个用于对话场景的智能助手，请正确、简洁、比较口语化地回答问题。你能够使用提供的tools（函数）来回答问题，有必要时需要从用户提问中抽取函数所需要的参数"}
]


def display_welcome():
    """Display a welcome message with instructions."""
    console.print(Panel.fit(
        "[bold cyan]Welcome to the AI Assistant[/bold cyan]\n\n"
        "This intelligent assistant can answer questions about:\n"
        "- [green]Current time[/green] (e.g., 'What time is it now?')\n"
        "- [green]Weather information[/green] (e.g., 'How's the weather in Shanghai today?')\n"
        "- [green]Route planning[/green] (e.g., 'How do I get from Fudan University to Wujiaochang?')\n\n"
        "Type [bold yellow]exit[/bold yellow], [bold yellow]quit[/bold yellow], or [bold yellow]bye[/bold yellow] to end the conversation.",
        title="🤖 AI Assistant",
        subtitle="Powered by DeepSeek AI",
        border_style="cyan"
    ))


def process_function_call(message):
    """Process a function call in the message."""
    if not message.tool_calls:
        return False
    
    # Display function call information
    for tool in message.tool_calls:
        function_name = tool.function.name
        function_arguments = json.loads(tool.function.arguments)
        
        console.print(Panel(
            f"[bold]Function:[/bold] [cyan]{function_name}[/cyan]\n"
            f"[bold]Arguments:[/bold] [yellow]{json.dumps(function_arguments, ensure_ascii=False, indent=2)}[/yellow]",
            title="🔧 Function Call",
            border_style="blue",
            expand=False
        ))
        
        # Special handling for route planning
        if "route_planning" in function_name and "address" in str(function_arguments):
            # We need to first get coordinates for addresses
            source_address = function_arguments.get("source_address")
            destination_address = function_arguments.get("destination_address")
            
            # Get coordinates for source
            if source_address:
                console.print(f"[bold green]Getting coordinates for [cyan]{source_address}[/cyan]...[/bold green]")
                source_result = function_registry.get(
                    "get_coordinates_from_address")({"address": source_address})
                source_data = json.loads(source_result)
                if source_data.get("status") == "1" and source_data.get("geocodes"):
                    source_location = source_data["geocodes"][0]["location"]
                    function_arguments["source"] = source_location
                    console.print(f"[green]Found coordinates: [cyan]{source_location}[/cyan][/green]")
            
            # Get coordinates for destination
            if destination_address:
                console.print(f"[bold green]Getting coordinates for [cyan]{destination_address}[/cyan]...[/bold green]")
                dest_result = function_registry.get("get_coordinates_from_address")({
                    "address": destination_address})
                dest_data = json.loads(dest_result)
                if dest_data.get("status") == "1" and dest_data.get("geocodes"):
                    dest_location = dest_data["geocodes"][0]["location"]
                    function_arguments["destination"] = dest_location
                    console.print(f"[green]Found coordinates: [cyan]{dest_location}[/cyan][/green]")
        
        # Execute function and get result
        console.print(f"[bold green]Executing function [cyan]{function_name}[/cyan]...[/bold green]")
        function_result = function_registry.get(
            function_name)(function_arguments)
        console.print("[green]Function executed successfully[/green]")
        
        # Add tool response to messages
        messages.append(
            {"role": "tool", "tool_call_id": tool.id, "content": function_result})
    
    return True


def stream_output(response_stream):
    """Stream the response with a nice animation."""
    full_response = ""
    
    # Create a panel for the response that will be updated
    response_panel = Panel("", title="🤖 Response", border_style="green")
    
    # Use Live display to update the panel in real-time
    with Live(response_panel, refresh_per_second=10, console=console) as live:
        for chunk in response_stream:
            if chunk.choices[0].delta.content:
                content_chunk = chunk.choices[0].delta.content
                full_response += content_chunk
                
                # Update the panel with the current response
                response_panel = Panel(
                    full_response, 
                    title="🤖 Response", 
                    border_style="green"
                )
                live.update(response_panel)
    
    return full_response


def main():
    """Main function to run the assistant."""
    display_welcome()

    # Show available capabilities
    capabilities = Table(title="Available Capabilities", box=box.ROUNDED)
    capabilities.add_column("Category", style="cyan")
    capabilities.add_column("Examples", style="green")

    capabilities.add_row("Time", "What time is it now?")
    capabilities.add_row(
        "Weather", "How's the weather in Shanghai?\nWhat's the weather forecast for Beijing?")
    capabilities.add_row(
        "Route Planning", "How do I get from Fudan University to Wujiaochang?\nWhat's the best way to travel from Shanghai to Beijing?")

    console.print(capabilities)

    # Main conversation loop
    conversation_count = 0
    while True:
        # Add a separator between conversations
        if conversation_count > 0:
            console.rule("[bold blue]New Query[/bold blue]")

        # Get user input with a stylish prompt
        user_input = Prompt.ask("\n[bold yellow]Q[/bold yellow]")

        # Exit condition
        if user_input.lower() in ["exit", "quit", "bye"]:
            console.print(
                "[bold cyan]Thank you for using the AI Assistant. Goodbye![/bold cyan]")
            break

        # Add user message to conversation history
        messages.append({"role": "user", "content": user_input})
        
        # Get initial response from model
        console.print("[bold green]Analyzing your query...[/bold green]")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=function_desc
        )
        
        message = response.choices[0].message

        # Add assistant message to conversation history
        messages.append(
            {"role": "assistant", "content": message.content, "tool_calls": message.tool_calls})

        # Check if we need to call a function
        if process_function_call(message):
            # If a function was called, generate a new response with the function result
            console.print("[bold yellow]A[/bold yellow]: ", end="")
            
            # Get response with function results
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=function_desc,
                stream=True
            )
            
            # Process streaming response - no nested status context here
            full_response = stream_output(response)
            
            # Update the last assistant message with the new content
            messages[-2]["content"] = full_response
        else:
            # If no function call was needed, just print the response
            console.print(
                f"[bold yellow]A[/bold yellow]: [green]{message.content}[/green]")

        conversation_count += 1


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print(
            "[bold red]\nProgram interrupted by user. Exiting...[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
