import requests
import json

def query_weather(key, city, extensions="all", output="JSON"):
    base_url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": key,
        "city": city,
        "extensions": extensions,
        "output": output
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()  # 返回JSON格式的查询结果
    else:
        return "请求失败，状态码: " + str(response.status_code)

# 使用实例
key = "e2d295172ba5aa4124aea68810670dd6"  # 你的API密钥
city = "440114"  # 花都区的adcode

# 查询花都区的天气预报
weather_info = query_weather(key, city, "all")  # 这里使用"all"获取天气预报，可改为"base"获取实况天气
print(weather_info)

formatted_weather_info = json.dumps(weather_info, indent=4, ensure_ascii=False)
print(formatted_weather_info)