from functionCallList import *


function_registry = {
    "get_time": get_time,
    "get_weather": get_weather,
    "get_coordinates_from_address": get_coordinates_from_address,
    "get_walking_route_planning": get_walking_route_planning,
    "get_public_transportation_route_planning": get_public_transportation_route_planning,
    "get_drive_route_planning": get_drive_route_planning,
    "get_bicycling_route_planning": get_bicycling_route_planning
}

function_desc = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "获取当前时间"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定地点的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "需要查询天气的地点，如杭州、上海、北京等"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_coordinates_from_address",
            "description": "将地址转换为经纬度坐标",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "详细地址，如复旦大学江湾校区、北京天安门等"
                    }
                },
                "required": ["address"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_walking_route_planning",
            "description": "获取步行路线规划",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "起点经纬度坐标，格式为'经度,纬度'"
                    },
                    "destination": {
                        "type": "string",
                        "description": "终点经纬度坐标，格式为'经度,纬度'"
                    },
                    "source_address": {
                        "type": "string",
                        "description": "起点地址，如复旦大学江湾校区"
                    },
                    "destination_address": {
                        "type": "string",
                        "description": "终点地址，如五角场"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_public_transportation_route_planning",
            "description": "获取公共交通路线规划",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "起点经纬度坐标，格式为'经度,纬度'"
                    },
                    "destination": {
                        "type": "string",
                        "description": "终点经纬度坐标，格式为'经度,纬度'"
                    },
                    "city": {
                        "type": "string",
                        "description": "城市名称，如上海、北京等"
                    },
                    "source_address": {
                        "type": "string",
                        "description": "起点地址，如复旦大学江湾校区"
                    },
                    "destination_address": {
                        "type": "string",
                        "description": "终点地址，如五角场"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_drive_route_planning",
            "description": "获取驾车路线规划",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "起点经纬度坐标，格式为'经度,纬度'"
                    },
                    "destination": {
                        "type": "string",
                        "description": "终点经纬度坐标，格式为'经度,纬度'"
                    },
                    "source_address": {
                        "type": "string",
                        "description": "起点地址，如复旦大学江湾校区"
                    },
                    "destination_address": {
                        "type": "string",
                        "description": "终点地址，如五角场"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_bicycling_route_planning",
            "description": "获取骑行路线规划",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "起点经纬度坐标，格式为'经度,纬度'"
                    },
                    "destination": {
                        "type": "string",
                        "description": "终点经纬度坐标，格式为'经度,纬度'"
                    },
                    "source_address": {
                        "type": "string",
                        "description": "起点地址，如复旦大学江湾校区"
                    },
                    "destination_address": {
                        "type": "string",
                        "description": "终点地址，如五角场"
                    }
                },
                "required": []
            }
        }
    }
]
