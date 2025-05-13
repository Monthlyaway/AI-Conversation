import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Mock data for testing without API keys
class MockData:
    @staticmethod
    def get_weather_data(location):
        """返回模拟的天气数据"""
        weather_data = {
            "location": {
                "name": location,
                "region": "",
                "country": "China",
                "lat": 30.25,
                "lon": 120.17,
                "tz_id": "Asia/Shanghai",
                "localtime_epoch": 1621324800,
                "localtime": datetime.now().strftime("%Y-%m-%d %H:%M")
            },
            "current": {
                "last_updated_epoch": 1621324800,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "temp_c": 23,
                "temp_f": 73.4,
                "is_day": 1,
                "condition": {
                    "text": "晴天",
                    "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
                    "code": 1000
                },
                "wind_mph": 6.9,
                "wind_kph": 11.2,
                "wind_degree": 150,
                "wind_dir": "SSE",
                "pressure_mb": 1012,
                "pressure_in": 29.9,
                "precip_mm": 0,
                "precip_in": 0,
                "humidity": 78,
                "cloud": 25,
                "feelslike_c": 24.8,
                "feelslike_f": 76.6,
                "vis_km": 10,
                "vis_miles": 6,
                "uv": 5,
                "gust_mph": 10.5,
                "gust_kph": 16.9
            }
        }
        return weather_data
    
    @staticmethod
    def get_coordinates_data(address):
        """返回模拟的地址坐标数据"""
        # 常见地点的模拟数据
        coordinates_map = {
            "复旦大学江湾校区": "121.503893,31.338047",
            "复旦大学": "121.503893,31.338047",
            "五角场": "121.514388,31.299379",
            "上海": "121.473701,31.230416",
            "北京": "116.407395,39.904211",
            "杭州": "120.155070,30.274084",
            "广州": "113.264434,23.129162",
            "深圳": "114.057868,22.543099",
            "天安门": "116.397452,39.908957",
            "外滩": "121.490317,31.236305",
            "东方明珠": "121.499705,31.239695",
        }
        
        # 尝试查找匹配的地址
        for key in coordinates_map:
            if key in address:
                location = coordinates_map[key]
                break
        else:
            # 如果没有匹配，返回上海中心的坐标
            location = "121.473701,31.230416"
            
        return {
            "status": "1",
            "info": "OK",
            "infocode": "10000",
            "count": "1",
            "geocodes": [
                {
                    "formatted_address": address,
                    "country": "中国",
                    "province": "上海市",
                    "citycode": "021",
                    "city": "上海市",
                    "district": "杨浦区",
                    "township": [],
                    "neighborhood": {"name": [], "type": []},
                    "building": {"name": [], "type": []},
                    "adcode": "310110",
                    "street": [],
                    "number": [],
                    "location": location,
                    "level": "兴趣点"
                }
            ]
        }
    
    @staticmethod
    def get_route_data(source, destination, route_type="walking"):
        """返回模拟的路线规划数据"""
        # 计算两点之间的直线距离（简化版）
        def calculate_distance(src, dst):
            # 提取经度和纬度
            src_lon, src_lat = map(float, src.split(","))
            dst_lon, dst_lat = map(float, dst.split(","))
            
            # 简单的距离计算（非实际地理距离）
            import math
            return math.sqrt((src_lon - dst_lon)**2 + (src_lat - dst_lat)**2) * 100000  # 转换为米
        
        # 计算距离（米）
        distance = calculate_distance(source, destination)
        
        # 根据路线类型设置不同的速度和描述
        route_info = {
            "walking": {
                "speed": 1.2,  # 步行速度 m/s
                "description": f"沿XX路步行约{int(distance/10)*10}米，到达目的地",
                "type": "步行"
            },
            "driving": {
                "speed": 8.3,  # 驾车速度 m/s (约30km/h)
                "description": f"驾车沿XX路行驶约{int(distance/100)*100}米，到达目的地",
                "type": "驾车"
            },
            "bicycling": {
                "speed": 3.0,  # 骑行速度 m/s
                "description": f"骑行沿XX路行驶约{int(distance/10)*10}米，到达目的地",
                "type": "骑行"
            },
            "transit": {
                "speed": 5.0,  # 公交速度 m/s
                "description": f"乘坐地铁X号线，经过3站，换乘Y路公交车，到达目的地",
                "type": "公共交通"
            }
        }
        
        info = route_info.get(route_type, route_info["walking"])
        duration = int(distance / info["speed"])  # 秒
        
        # 构建通用的返回数据
        result = {
            "status": "1",
            "info": "OK",
            "infocode": "10000",
            "count": "1",
            "route": {
                "origin": source,
                "destination": destination,
                "distance": str(int(distance)),
                "duration": str(duration),
                "steps": [
                    {
                        "instruction": info["description"],
                        "distance": str(int(distance)),
                        "duration": str(duration),
                        "type": info["type"]
                    }
                ]
            }
        }
        
        return result


def get_time(parameters):
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_weather(parameters):
    """获取天气信息（模拟数据）"""
    try:
        location = parameters["location"]
        # 使用模拟数据
        data = MockData.get_weather_data(location)
        return json.dumps(data)
    except KeyError:
        return "缺失函数参数，请提供所有要求参数后重试"
    except Exception as e:
        print(e)
        return "获取天气信息失败，请重试"


def get_coordinates_from_address(parameters):
    """获取地址的坐标（模拟数据）"""
    try:
        address = parameters["address"]
        # 使用模拟数据
        data = MockData.get_coordinates_data(address)
        return json.dumps(data)
    except Exception as e:
        print(e)
        return "获取对应地址的位置经纬度失败，请重试"


def get_walking_route_planning(parameters):
    """获取步行路线规划（模拟数据）"""
    try:
        source = parameters["source"]
        destination = parameters["destination"]
        # 使用模拟数据
        data = MockData.get_route_data(source, destination, "walking")
        return json.dumps(data)
    except Exception as e:
        print(e)
        return "获取步行路径规划失败，请重试"


def get_public_transportation_route_planning(parameters):
    """获取公共交通路线规划（模拟数据）"""
    try:
        source = parameters["source"]
        destination = parameters["destination"]
        # 城市参数在模拟数据中不使用
        # 使用模拟数据
        data = MockData.get_route_data(source, destination, "transit")
        return json.dumps(data)
    except Exception as e:
        print(e)
        return "获取公共交通路径规划失败，请重试"


def get_drive_route_planning(parameters):
    """获取驾车路线规划（模拟数据）"""
    try:
        source = parameters["source"]
        destination = parameters["destination"]
        # 使用模拟数据
        data = MockData.get_route_data(source, destination, "driving")
        return json.dumps(data)
    except Exception as e:
        print(e)
        return "获取驾车路径规划失败，请重试"


def get_bicycling_route_planning(parameters):
    """获取骑行路线规划（模拟数据）"""
    try:
        source = parameters["source"]
        destination = parameters["destination"]
        # 使用模拟数据
        data = MockData.get_route_data(source, destination, "bicycling")
        return json.dumps(data)
    except Exception as e:
        print(e)
        return "获取骑行路径规划失败，请重试" 