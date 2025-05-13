import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
# 请在.env文件中设置你在 weatherapi.com 上申请的 API key
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
# 请在.env文件中设置你在高德开放平台上申请的 Web服务 API key
AMAP_API_KEY = os.getenv("AMAP_API_KEY", "")


def get_time(parameters):
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_weather(parameters):
    try:
        url = f"http://api.weatherapi.com/v1/current.json"
        req_params = {
            "key": WEATHER_API_KEY,
            "q": parameters["location"],
            "aqi": "no"
        }
        response = requests.get(url=url, params=req_params)
        if response.status_code == 200:
            data = response.json()
            # print("weather", data)
            return json.dumps(data)
        else:
            raise Exception("weatherapi 请求失败")
    except KeyError:
        return "缺失函数参数，请提供所有要求参数后重试"
    except Exception as e:
        print(e)
        return "获取天气信息失败，请重试"


def get_coordinates_from_address(parameters):
    try:
        url = f"https://restapi.amap.com/v3/geocode/geo"
        req_params = {
            "key": AMAP_API_KEY,
            "address": parameters["address"],
        }
        response = requests.get(url=url, params=req_params)
        if response.status_code == 200:
            data = response.json()
            return json.dumps(data)
        else:
            raise Exception("amap 请求地址经纬度失败")
    except Exception as e:
        print(e)
        return "获取对应地址的位置经纬度失败，请重试"


def get_walking_route_planning(parameters):
    try:
        url = f"https://restapi.amap.com/v3/direction/walking"
        req_params = {
            "key": AMAP_API_KEY,
            "origin": parameters["source"],
            "destination": parameters["destination"]
        }
        response = requests.get(url=url, params=req_params)
        if response.status_code == 200:
            data = response.json()
            return json.dumps(data)
        else:
            raise Exception("amap 请求步行路径规划失败")
    except Exception as e:
        print(e)
        return "获取步行路径规划失败，请重试"


def get_public_transportation_route_planning(parameters):
    try:
        url = f"https://restapi.amap.com/v3/direction/transit/integrated"
        req_params = {
            "key": AMAP_API_KEY,
            "origin": parameters["source"],
            "destination": parameters["destination"],
            "city": parameters["city"]
        }
        response = requests.get(url=url, params=req_params)
        if response.status_code == 200:
            data = response.json()
            return json.dumps(data)
        else:
            raise Exception("amap 请求公共交通路径规划失败")
    except Exception as e:
        print(e)
        return "获取公共交通路径规划失败，请重试"


def get_drive_route_planning(parameters):
    try:
        url = f"https://restapi.amap.com/v3/direction/driving"
        req_params = {
            "key": AMAP_API_KEY,
            "origin": parameters["source"],
            "destination": parameters["destination"],
        }
        response = requests.get(url=url, params=req_params)
        if response.status_code == 200:
            data = response.json()
            return json.dumps(data)
        else:
            raise Exception("amap 请求驾车路径规划失败")
    except Exception as e:
        print(e)
        return "获取驾车路径规划失败，请重试"


def get_bicycling_route_planning(parameters):
    try:
        url = f"https://restapi.amap.com/v4/direction/bicycling"
        req_params = {
            "key": AMAP_API_KEY,
            "origin": parameters["source"],
            "destination": parameters["destination"],
        }
        response = requests.get(url=url, params=req_params)
        if response.status_code == 200:
            data = response.json()
            return json.dumps(data)
        else:
            raise Exception("amap 请求骑行路径规划失败")
    except Exception as e:
        print(e)
        return "获取骑行路径规划失败，请重试"
