import json
import uuid
import httpx
from app.core.config import get_settings

settings = get_settings()


class OutfitAIService:
    """
    调用 DeepSeek API 生成穿搭推荐。
    TODO: 衣橱查询待接入数据库（目前用 stub 数据）。
    """

    async def recommend(self, scene: str, clothes: list[dict], weather: dict) -> dict:
        """
        1. 构建 prompt：天气 + 场景 + 衣橱单品列表
        2. 调用 DeepSeek /chat/completions
        3. 解析返回 JSON，包装成前端需要的 outfit 对象

        返回格式（前端期望）：
        {
            "id": str,
            "name": str,
            "description": str,
            "matchRate": int,
            "reason": str,
            "image": str
        }
        """
        if not settings.deepseek_api_key:
            return self._fallback_recommend(scene, clothes, weather)

        prompt = self._build_prompt(scene, clothes, weather)

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(
                    "https://api.deepseek.com/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.deepseek_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {
                                "role": "system",
                                "content": "你是时尚穿搭顾问，擅长根据天气和场景从用户衣橱中挑选最合适的搭配。请严格输出 JSON 格式，不要包含任何 markdown 代码块标记。",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.7,
                        "max_tokens": 512,
                    },
                )
                resp.raise_for_status()
                result = resp.json()
                content = result["choices"][0]["message"]["content"]

                # DeepSeek 可能返回 markdown 代码块，需要清理
                content = content.strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1] if "\n" in content else content
                    content = content.rsplit("\n", 1)[0] if "\n" in content else content
                    content = content.replace("```json", "").replace("```", "").strip()

                ai_result = json.loads(content)
                return {
                    "id": str(uuid.uuid4()),
                    "name": ai_result.get("name", "时尚穿搭"),
                    "description": ai_result.get("description", ""),
                    "matchRate": ai_result.get("matchRate", 85),
                    "reason": ai_result.get("reason", ""),
                    "image": ai_result.get("image", ""),
                }
            except Exception:
                return self._fallback_recommend(scene, clothes, weather)

    def _build_prompt(self, scene: str, clothes: list[dict], weather: dict) -> str:
        scene_names = {
            "commute": "通勤",
            "date": "约会",
            "casual": "休闲",
            "sports": "运动",
            "party": "派对",
        }
        scene_name = scene_names.get(scene, "日常")

        clothes_list = "\n".join(
            f"- {c.get('name', '未知')}（{c.get('category', '其他')}，颜色 {c.get('color', '未知')}）"
            for c in clothes
        )

        return (
            f"你是穿搭顾问。请根据以下信息为用户推荐一套穿搭：\n\n"
            f"场景：{scene_name}\n"
            f"天气：{weather.get('text', '晴')}，{weather.get('temp', '20')}°C\n"
            f"衣橱可用单品：\n{clothes_list}\n\n"
            f"要求：\n"
            f"1. 从衣橱中挑选合适的单品进行搭配\n"
            f"2. 给出穿搭名称、描述、匹配度（0-100）和推荐理由\n"
            f"3. 输出严格 JSON 格式：\n"
            f'{{"name":"穿搭名称","description":"简短描述","matchRate":85,"reason":"推荐理由"}}'
        )

    def _fallback_recommend(self, scene: str, clothes: list[dict], weather: dict) -> dict:
        scene_names = {
            "commute": "通勤",
            "date": "约会",
            "casual": "休闲",
            "sports": "运动",
            "party": "派对",
        }
        scene_name = scene_names.get(scene, "日常")
        return {
            "id": str(uuid.uuid4()),
            "name": f"{scene_name}风格穿搭",
            "description": f"根据{weather.get('text', '晴')}天气推荐，{len(clothes)}件单品自由搭配",
            "matchRate": 85,
            "reason": "基于你的衣橱单品和当前天气条件推荐",
            "image": "",
        }
