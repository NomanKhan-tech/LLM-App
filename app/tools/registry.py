from app.tools.weather_tool import get_weather
from app.tools.time_tool import get_time
from app.tools.calculator_tool import calculate

TOOL_REGISTRY = {
    "get_weather": get_weather,
    "get_time": get_time,
    "calculate": calculate,
}
