import os
import json
import logging
from dotenv import load_dotenv
from typing import Dict, List, Any

# Import functionCallList functions and registry
from functionCallList import *
import functionCallRegistry

# Import necessary LangChain components
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Set up logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API credentials from environment variables
API_KEY = os.getenv("API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "https://api.siliconflow.cn/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-V3")

# Check if API key is set
if not API_KEY:
    logger.error("Missing API_KEY in environment variables")
    print("Error: API_KEY is not set in the .env file. Please set it and try again.")
    exit(1)

# Define tools using LangChain's tool decorator


@tool
def get_current_time(dummy: str = "") -> str:
    """Get the current time."""
    logger.debug("Calling get_current_time function")
    return get_time({})


@tool
def get_weather_info(location: str) -> str:
    """Get weather information for a specific location."""
    logger.debug(f"Calling get_weather_info function for location: {location}")
    result = get_weather({"location": location})
    return result


@tool
def get_coordinates(address: str) -> str:
    """Convert an address to coordinates."""
    logger.debug(f"Calling get_coordinates function for address: {address}")
    result = get_coordinates_from_address({"address": address})
    return result


@tool
def get_walking_route(source_address: str, destination_address: str) -> str:
    """Get walking route between two locations."""
    logger.debug(
        f"Planning walking route from {source_address} to {destination_address}")

    # First get coordinates for source address
    source_result = get_coordinates_from_address({"address": source_address})
    source_data = json.loads(source_result)
    if source_data.get("status") != "1" or not source_data.get("geocodes"):
        return f"Could not find coordinates for {source_address}"
    source_location = source_data["geocodes"][0]["location"]

    # Then get coordinates for destination address
    dest_result = get_coordinates_from_address(
        {"address": destination_address})
    dest_data = json.loads(dest_result)
    if dest_data.get("status") != "1" or not dest_data.get("geocodes"):
        return f"Could not find coordinates for {destination_address}"
    dest_location = dest_data["geocodes"][0]["location"]

    # Get walking route
    result = get_walking_route_planning({
        "source": source_location,
        "destination": dest_location
    })
    return result


@tool
def get_public_transit_route(source_address: str, destination_address: str, city: str) -> str:
    """Get public transportation route between two locations."""
    logger.debug(
        f"Planning public transit route from {source_address} to {destination_address} in {city}")

    # First get coordinates for source address
    source_result = get_coordinates_from_address({"address": source_address})
    source_data = json.loads(source_result)
    if source_data.get("status") != "1" or not source_data.get("geocodes"):
        return f"Could not find coordinates for {source_address}"
    source_location = source_data["geocodes"][0]["location"]

    # Then get coordinates for destination address
    dest_result = get_coordinates_from_address(
        {"address": destination_address})
    dest_data = json.loads(dest_result)
    if dest_data.get("status") != "1" or not dest_data.get("geocodes"):
        return f"Could not find coordinates for {destination_address}"
    dest_location = dest_data["geocodes"][0]["location"]

    # Get public transit route
    result = get_public_transportation_route_planning({
        "source": source_location,
        "destination": dest_location,
        "city": city
    })
    return result


@tool
def get_driving_route(source_address: str, destination_address: str) -> str:
    """Get driving route between two locations."""
    logger.debug(
        f"Planning driving route from {source_address} to {destination_address}")

    # First get coordinates for source address
    source_result = get_coordinates_from_address({"address": source_address})
    source_data = json.loads(source_result)
    if source_data.get("status") != "1" or not source_data.get("geocodes"):
        return f"Could not find coordinates for {source_address}"
    source_location = source_data["geocodes"][0]["location"]

    # Then get coordinates for destination address
    dest_result = get_coordinates_from_address(
        {"address": destination_address})
    dest_data = json.loads(dest_result)
    if dest_data.get("status") != "1" or not dest_data.get("geocodes"):
        return f"Could not find coordinates for {destination_address}"
    dest_location = dest_data["geocodes"][0]["location"]

    # Get driving route
    result = get_drive_route_planning({
        "source": source_location,
        "destination": dest_location
    })
    return result


@tool
def get_biking_route(source_address: str, destination_address: str) -> str:
    """Get biking route between two locations."""
    logger.debug(
        f"Planning biking route from {source_address} to {destination_address}")

    # First get coordinates for source address
    source_result = get_coordinates_from_address({"address": source_address})
    source_data = json.loads(source_result)
    if source_data.get("status") != "1" or not source_data.get("geocodes"):
        return f"Could not find coordinates for {source_address}"
    source_location = source_data["geocodes"][0]["location"]

    # Then get coordinates for destination address
    dest_result = get_coordinates_from_address(
        {"address": destination_address})
    dest_data = json.loads(dest_result)
    if dest_data.get("status") != "1" or not dest_data.get("geocodes"):
        return f"Could not find coordinates for {destination_address}"
    dest_location = dest_data["geocodes"][0]["location"]

    # Get biking route
    result = get_bicycling_route_planning({
        "source": source_location,
        "destination": dest_location
    })
    return result


def main():
    """Main function to run the application."""
    # Define tools
    tools = [
        get_current_time,
        get_weather_info,
        get_coordinates,
        get_walking_route,
        get_public_transit_route,
        get_driving_route,
        get_biking_route,
    ]

    # Initialize DeepSeek LLM with the OpenAI-compatible API
    model = ChatOpenAI(
        model=MODEL_NAME,
        api_key=API_KEY,
        base_url=BASE_URL,
        streaming=True
    )

    # Create memory for conversation history
    memory = MemorySaver()

    # Create the agent using LangGraph's reactive agent pattern
    agent_executor = create_react_agent(model, tools, checkpointer=memory)

    # Print welcome message
    print("\n=== AI Assistant with LangChain ===")
    print("This assistant can answer questions about:")
    print("- Current time")
    print("- Weather information (e.g., 'How's the weather in Shanghai today?')")
    print("- Route planning (e.g., 'How do I get from Fudan University to Wujiaochang?')")
    print("Type 'exit', 'quit', or 'bye' to end the conversation.\n")

    # Generate a unique thread ID for this conversation
    thread_id = "conversation-thread-1"
    config = {"configurable": {"thread_id": thread_id}}

    # Main conversation loop
    while True:
        # Get user input
        user_input = input("Q: ")

        # Exit condition
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Thank you for using the AI Assistant. Goodbye!")
            break

        try:
            # Format the input for the agent
            agent_input = {"messages": [HumanMessage(content=user_input)]}

            # # Option 1: Stream with values mode - This shows complete messages
            for step in agent_executor.stream(
                agent_input,
                config,
                stream_mode="values"
            ):
                if "messages" in step and len(step["messages"]) > 0:
                    step["messages"][-1].pretty_print()

            # Option 2: Stream with messages mode - This shows token-by-token
            # Uncomment this and comment out Option 1 to switch modes

            # for step, metadata in agent_executor.stream(
            #     agent_input,
            #     config,
            #     stream_mode="messages"
            # ):
            #     if metadata["langgraph_node"] == "agent" and (text := step.text()):
            #         print(text, end="|")
            # print()  # Add a newline at the end

        except Exception as e:
            logger.error(f"Error during agent execution: {str(e)}")
            print(f"\nError: {str(e)}")


if __name__ == "__main__":
    main()
