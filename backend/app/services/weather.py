import httpx
from app.core.config import get_settings

settings = get_settings()

# 常见城市 Location ID（和风天气）
_CITY_IDS = {
    "北京": "101010100",
    "上海": "101020100",
    "广州": "101280101",
    "深圳": "101280601",
    "杭州": "101210101",
    "成都": "101270101",
    "武汉": "101200101",
    "西安": "101110101",
    "南京": "101190101",
    "重庆": "101040100",
}


class WeatherService:
    """
    和风天气 API 封装（新版）。
    每个开发者有独立的 API Host，在控制台查看。
    认证方式：请求头 X-QW-Api-Key。
    TODO: 接入真实衣橱数据库后，location 应从用户 profile 读取。
    """

    async def get_current(self, location: str = "深圳") -> dict:
        """
        获取实时天气。直接通过城市名映射表查询 LocationID，无需额外调用搜索 API。

        返回: {"temp": "24", "text": "阴", "windScale": "5", "humidity": "84"}
        如果 API key/host 未配置或调用失败，返回 fallback 数据。
        """
        if not settings.hefeng_api_key or not settings.hefeng_api_host:
            return self._fallback_weather(location)

        location_id = _CITY_IDS.get(location)
        if not location_id:
            return self._fallback_weather(location)

        headers = {"X-QW-Api-Key": settings.hefeng_api_key}
        host = settings.hefeng_api_host
        url = f"https://{host}/v7/weather/now?location={location_id}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                if data.get("code") != "200":
                    return self._fallback_weather(location)

                now = data.get("now", {})
                return {
                    "temp": now.get("temp", "22"),
                    "text": now.get("text", "多云"),
                    "windScale": now.get("windScale", "2"),
                    "humidity": now.get("humidity", "50"),
                }
            except Exception:
                return self._fallback_weather(location)

    def _fallback_weather(self, location: str) -> dict:
        return {
            "temp": "22",
            "text": "多云",
            "windScale": "2",
            "humidity": "60",
            "_source": "fallback",
        }
