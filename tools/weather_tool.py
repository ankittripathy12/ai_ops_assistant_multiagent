import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from tools.base_tool import BaseTool
except ImportError:
    from .base_tool import BaseTool

from config import Config


class WeatherTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="weather",
            description="Fetch current weather information for a city"
        )
        self.base_url = Config.WEATHER_API_URL

    def execute(self, **kwargs) -> dict:
        city = kwargs.get("city")
        if not city:
            # Try to extract city from other parameters
            city = kwargs.get("location") or kwargs.get("place") or "London"

        return self.get_current_weather(city)

    def get_current_weather(self, city: str) -> dict:
        """Get current weather for a city"""
        params = {
            "key": Config.WEATHER_API_KEY,
            "q": city,
            "aqi": "no"
        }

        try:
            response = self.make_request(
                method="GET",
                url=self.base_url,
                params=params
            )

            current = response.get("current", {})
            location = response.get("location", {})

            return {
                "city": location.get("name"),
                "country": location.get("country"),
                "temperature_c": current.get("temp_c"),
                "temperature_f": current.get("temp_f"),
                "condition": current.get("condition", {}).get("text"),
                "humidity": current.get("humidity"),
                "wind_kph": current.get("wind_kph"),
                "last_updated": current.get("last_updated")
            }
        except Exception as e:
            return {
                "error": str(e),
                "city": city
            }