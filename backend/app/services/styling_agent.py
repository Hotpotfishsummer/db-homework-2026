from __future__ import annotations

import json
import uuid
from typing import Any

from app.core.config import get_settings
from app.services.weather import WeatherService
from app.services.wardrobe_stub import WardrobeService

settings = get_settings()

try:
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI

    LANGCHAIN_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    AgentExecutor = None
    create_tool_calling_agent = None
    ChatPromptTemplate = None
    MessagesPlaceholder = None
    tool = None
    ChatOpenAI = None
    LANGCHAIN_AVAILABLE = False


class StylingAgentService:
    """LangChain-powered orchestration layer for wardrobe advice."""

    def __init__(self):
        self.weather_service = WeatherService()
        self.wardrobe_service = WardrobeService()

    async def generate_daily_tip(self, user_id: str | int | None = None, location: str | None = None) -> dict:
        weather = await self.weather_service.get_current(location=location or "深圳")
        wardrobe_items = await self.wardrobe_service.get_by_ids(str(user_id) if user_id is not None else "0", [1, 2, 3])

        if not self._can_use_agent():
            return self._fallback_daily_tip(weather, wardrobe_items)

        tools = self._build_daily_tip_tools(user_id=user_id, location=location, weather=weather, wardrobe_items=wardrobe_items)
        result = await self._run_agent(
            system_prompt=self._daily_tip_system_prompt(),
            user_prompt=self._daily_tip_user_prompt(user_id=user_id, location=location),
            tools=tools,
        )
        return self._normalize_daily_tip_result(result, weather=weather, wardrobe_items=wardrobe_items)

    async def recommend_outfit(
        self,
        scene: str,
        wardrobe_ids: list[int],
        user_id: str | int | None = None,
        location: str | None = None,
    ) -> dict:
        weather = await self.weather_service.get_current(location=location or "深圳")
        clothes = await self.wardrobe_service.get_by_ids(str(user_id) if user_id is not None else "0", wardrobe_ids)

        if not self._can_use_agent():
            return self._fallback_outfit(scene, clothes, weather)

        tools = self._build_outfit_tools(user_id=user_id, location=location, scene=scene, wardrobe_ids=wardrobe_ids, weather=weather, clothes=clothes)
        result = await self._run_agent(
            system_prompt=self._outfit_system_prompt(),
            user_prompt=self._outfit_user_prompt(scene=scene, wardrobe_ids=wardrobe_ids, user_id=user_id, location=location),
            tools=tools,
        )
        return self._normalize_outfit_result(result, scene=scene, weather=weather, clothes=clothes)

    def _can_use_agent(self) -> bool:
        return bool(
            LANGCHAIN_AVAILABLE
            and settings.llm_api_key
            and settings.llm_api_base
            and settings.llm_model
        )

    def _build_llm(self):
        if not self._can_use_agent():
            raise RuntimeError("LangChain LLM is not available")
        return ChatOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_api_base,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

    def _run_agent(self, system_prompt: str, user_prompt: str, tools: list[Any]) -> Any:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        llm = self._build_llm()
        agent = create_tool_calling_agent(llm, tools, prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            max_iterations=settings.agent_max_iterations,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )
        return executor.ainvoke({"input": user_prompt})

    def _build_daily_tip_tools(
        self,
        user_id: str | int | None,
        location: str | None,
        weather: dict,
        wardrobe_items: list[dict],
    ) -> list[Any]:
        if not LANGCHAIN_AVAILABLE:
            return []

        fallback_location = location or "深圳"
        return [
            self._weather_tool(weather_snapshot=weather, fallback_location=fallback_location),
            self._wardrobe_tool(items=wardrobe_items),
            self._user_profile_tool(user_id=user_id, location=fallback_location),
            self._style_rules_tool(),
        ]

    def _build_outfit_tools(
        self,
        user_id: str | int | None,
        location: str | None,
        scene: str,
        wardrobe_ids: list[int],
        weather: dict,
        clothes: list[dict],
    ) -> list[Any]:
        if not LANGCHAIN_AVAILABLE:
            return []

        fallback_location = location or "深圳"
        return [
            self._weather_tool(weather_snapshot=weather, fallback_location=fallback_location),
            self._wardrobe_tool(items=clothes, ids=wardrobe_ids),
            self._user_profile_tool(user_id=user_id, location=fallback_location),
            self._history_tool(),
            self._style_rules_tool(scene=scene),
        ]

    def _weather_tool(self, weather_snapshot: dict, fallback_location: str):
        @tool("get_weather")
        async def get_weather(city: str | None = None) -> str:
            current = weather_snapshot if not city or city == fallback_location else await self.weather_service.get_current(location=city)
            return json.dumps(current, ensure_ascii=False)

        return get_weather

    def _wardrobe_tool(self, items: list[dict], ids: list[int] | None = None):
        payload: dict[str, Any] = {"items": items, "count": len(items)}
        if ids is not None:
            payload["ids"] = ids

        @tool("get_wardrobe_items")
        async def get_wardrobe_items() -> str:
            return json.dumps(payload, ensure_ascii=False)

        return get_wardrobe_items

    def _user_profile_tool(self, user_id: str | int | None, location: str):
        @tool("get_user_profile")
        async def get_user_profile() -> str:
            profile = {
                "user_id": user_id,
                "display_name": "匿名用户",
                "style_preference": "日常简洁",
                "location": location,
            }
            return json.dumps(profile, ensure_ascii=False)

        return get_user_profile

    def _history_tool(self):
        @tool("get_history_recommendations")
        async def get_history_recommendations() -> str:
            history = {
                "items": [],
                "note": "当前为占位历史推荐接口，后续将接入 recommendation_repo。",
            }
            return json.dumps(history, ensure_ascii=False)

        return get_history_recommendations

    def _style_rules_tool(self, scene: str | None = None):
        @tool("get_style_rules")
        async def get_style_rules() -> str:
            rules = {
                "scene": scene,
                "priority": ["根据天气", "结合衣橱可用项", "给出可执行建议"] if scene is None else ["天气适配", "场景一致性", "衣橱可用性"],
                "note": "当前为占位规则，后续可替换为用户历史与偏好驱动的规则引擎。",
            }
            return json.dumps(rules, ensure_ascii=False)

        return get_style_rules

    def _daily_tip_system_prompt(self) -> str:
        return (
            "你是一个穿搭建议 Agent。你必须优先调用工具获取天气、衣橱、用户资料和规则，再输出简洁可执行的每日建议。"
            "最终只输出严格 JSON，不要输出 markdown。字段格式：{\"tip\": string, \"weather_summary\": string, \"wardrobe_items_considered\": number, \"generated_by\": string, \"tool_summary\": string[]}"
        )

    def _outfit_system_prompt(self) -> str:
        return (
            "你是一个穿搭编排 Agent。你必须优先调用工具获取天气、衣橱、用户资料、历史推荐和规则，再生成结构化穿搭建议。"
            "最终只输出严格 JSON，不要输出 markdown。字段格式：{\"name\": string, \"description\": string, \"matchRate\": number, \"reason\": string, \"image\": string, \"selectedItems\": array, \"weatherSummary\": string, \"toolSummary\": string[], \"generatedBy\": string}"
        )

    def _daily_tip_user_prompt(self, user_id: str | int | None, location: str | None) -> str:
        return (
            f"用户ID: {user_id}\n"
            f"位置: {location or '深圳'}\n"
            "请产出今天的穿搭建议，语气简洁，强调可执行性。"
        )

    def _outfit_user_prompt(self, scene: str, wardrobe_ids: list[int], user_id: str | int | None, location: str | None) -> str:
        return (
            f"用户ID: {user_id}\n"
            f"场景: {scene}\n"
            f"衣橱单品ID: {wardrobe_ids}\n"
            f"位置: {location or '深圳'}\n"
            "请生成一套穿搭推荐，强调为何适合当前场景和天气。"
        )

    def _normalize_daily_tip_result(self, result: dict, weather: dict, wardrobe_items: list[dict]) -> dict:
        output = self._parse_json_output(result.get("output", ""))
        tip = output.get("tip") or output.get("description") or self._default_tip(weather)
        return {
            "tip": tip,
            "weather_summary": output.get("weather_summary") or self._weather_summary(weather),
            "wardrobe_items_considered": output.get("wardrobe_items_considered", len(wardrobe_items)),
            "generated_by": output.get("generated_by", "langchain-agent" if self._can_use_agent() else "fallback"),
            "tool_summary": output.get("tool_summary", self._summarize_intermediate_steps(result.get("intermediate_steps", []))),
            "raw_output": result.get("output", ""),
        }

    def _normalize_outfit_result(self, result: dict, scene: str, weather: dict, clothes: list[dict]) -> dict:
        output = self._parse_json_output(result.get("output", ""))
        fallback = self._fallback_outfit(scene, clothes, weather)
        merged = {**fallback, **output}
        merged.setdefault("id", str(uuid.uuid4()))
        merged.setdefault("scene", scene)
        merged.setdefault("toolSummary", self._summarize_intermediate_steps(result.get("intermediate_steps", [])))
        merged.setdefault("weatherSummary", self._weather_summary(weather))
        merged.setdefault("generatedBy", "langchain-agent" if self._can_use_agent() else "fallback")
        merged.setdefault("selectedItems", [])
        merged.setdefault("raw_output", result.get("output", ""))
        return merged

    def _parse_json_output(self, raw_output: str) -> dict:
        if not raw_output:
            return {}
        content = raw_output.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content
            content = content.rsplit("\n", 1)[0] if "\n" in content else content
            content = content.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(content)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _summarize_intermediate_steps(self, intermediate_steps: list[Any]) -> list[str]:
        summary: list[str] = []
        for step in intermediate_steps or []:
            try:
                action = step[0]
                observation = step[1]
                tool_name = getattr(action, "tool", None) or getattr(action, "tool_name", None) or "tool"
                summary.append(f"{tool_name}: {str(observation)[:120]}")
            except Exception:
                summary.append("tool step captured")
        return summary

    def _weather_summary(self, weather: dict) -> str:
        text = weather.get("text", "晴")
        temp = weather.get("temp", "22")
        return f"{text}，{temp}°C"

    def _default_tip(self, weather: dict) -> str:
        return f"今天是{self._weather_summary(weather)}，优先选择舒适、适配场景的基础款，并按层次搭配。"

    def _fallback_daily_tip(self, weather: dict, wardrobe_items: list[dict]) -> dict:
        return {
            "tip": self._default_tip(weather),
            "weather_summary": self._weather_summary(weather),
            "wardrobe_items_considered": len(wardrobe_items),
            "generated_by": "fallback",
            "tool_summary": ["weather fallback", "wardrobe fallback"],
        }

    def _fallback_outfit(self, scene: str, clothes: list[dict], weather: dict) -> dict:
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
            "selectedItems": [item.get("id") for item in clothes if item.get("id") is not None],
            "weatherSummary": self._weather_summary(weather),
            "toolSummary": ["weather fallback", "wardrobe fallback"],
            "generatedBy": "fallback",
        }