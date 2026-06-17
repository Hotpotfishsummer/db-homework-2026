"""Outfit recommendation agent (衣橱内组合).

Refactored to inherit LLM/agent plumbing from ``BaseAgentService`` (see
``base_agent.py``). This module owns:

- Outfit-specific tool set (history, style rules, save_recommendation)
- Outfit system/user prompts
- JSON normalization to the outfit response shape
- Fallback templates
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base_agent import (
    BaseAgentService,
    LANGCHAIN_AVAILABLE,
    tool,
)
from app.core.user_llm import UserLLMConfig
from db.repositories.recommendation_repo import RecommendationRepository

logger = logging.getLogger(__name__)


class StylingAgentService(BaseAgentService):
    """LangChain-powered outfit recommendation service (衣橱内组合)."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.recommendation_repo = RecommendationRepository(session)

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------
    async def generate_daily_tip(
        self,
        user_id: str | int | None = None,
        location: str | None = None,
        user_llm: "UserLLMConfig | None" = None,
    ) -> dict:
        import time
        started_at = time.perf_counter()
        resolved_user_id = int(user_id) if user_id is not None else 0
        resolved_location = location or "深圳"
        logger.info("Daily tip generation started: user_id=%s location=%s", resolved_user_id, resolved_location)

        if not self._can_use_agent(user_llm=user_llm):
            logger.warning("Daily tip generation falling back because agent is unavailable")
            weather = await self.weather_service.get_current(location=resolved_location)
            return self._fallback_daily_tip(weather, [])

        tools = self._build_daily_tip_tools(resolved_user_id, resolved_location)
        logger.info("Daily tip agent tools prepared: tool_count=%s", len(tools))

        result = await self._run_agent(
            system_prompt=self._daily_tip_system_prompt(),
            user_prompt=self._daily_tip_user_prompt(user_id=resolved_user_id, location=resolved_location),
            tools=tools,
            user_llm=user_llm,
        )
        normalized = self._normalize_daily_tip_result(result, resolved_user_id)
        logger.info(
            "Daily tip generation finished: generated_by=%s elapsed_ms=%.2f",
            normalized.get("generated_by"),
            (time.perf_counter() - started_at) * 1000,
        )
        return normalized

    async def recommend_outfit(
        self,
        scene: str,
        wardrobe_ids: list[int] | None = None,
        user_id: str | int | None = None,
        location: str | None = None,
        user_llm: "UserLLMConfig | None" = None,
        body_profile: dict | None = None,
    ) -> dict:
        import time
        started_at = time.perf_counter()
        resolved_user_id = int(user_id) if user_id is not None else 0
        resolved_location = location or "深圳"
        self.request_body_profile = body_profile if isinstance(body_profile, dict) else None
        logger.info(
            "Outfit recommendation started: scene=%s wardrobe_count=%s user_id=%s location=%s",
            scene,
            len(wardrobe_ids or []),
            resolved_user_id,
            resolved_location,
        )

        if not self._can_use_agent(user_llm=user_llm):
            logger.warning("Outfit recommendation falling back because agent is unavailable")
            weather = await self.weather_service.get_current(location=resolved_location)
            return self._fallback_outfit(scene, [], weather)

        tools = self._build_outfit_tools(resolved_user_id, resolved_location, scene, wardrobe_ids or [])
        logger.info("Outfit recommendation agent tools prepared: tool_count=%s", len(tools))

        result = await self._run_agent(
            system_prompt=self._outfit_system_prompt(),
            user_prompt=self._outfit_user_prompt(
                scene=scene, wardrobe_ids=wardrobe_ids or [], user_id=resolved_user_id, location=resolved_location
            ),
            tools=tools,
            user_llm=user_llm,
        )
        normalized = self._normalize_outfit_result(result, scene=scene, user_id=resolved_user_id)
        logger.info(
            "Outfit recommendation finished: generated_by=%s matchRate=%s elapsed_ms=%.2f",
            normalized.get("generatedBy"),
            normalized.get("matchRate"),
            (time.perf_counter() - started_at) * 1000,
        )
        return normalized

    # ------------------------------------------------------------------
    # Tool builders (outfit-specific)
    # ------------------------------------------------------------------
    def _build_daily_tip_tools(self, user_id: int, location: str) -> list[Any]:
        if not LANGCHAIN_AVAILABLE:
            return []
        return [
            self._make_weather_tool(location=location),
            self._make_search_wardrobe_tool(user_id=user_id),
            self._count_wardrobe_tool(user_id=user_id),
            self._get_wardrobe_items_tool(user_id=user_id),
            self._make_user_profile_tool(user_id=user_id),
            self._history_tool(user_id=user_id),
        ]

    def _build_outfit_tools(
        self,
        user_id: int,
        location: str,
        scene: str,
        wardrobe_ids: list[int],
    ) -> list[Any]:
        if not LANGCHAIN_AVAILABLE:
            return []
        return [
            self._make_weather_tool(location=location),
            self._make_search_wardrobe_tool(user_id=user_id),
            self._get_wardrobe_items_tool(user_id=user_id),
            self._count_wardrobe_tool(user_id=user_id),
            self._make_user_profile_tool(user_id=user_id),
            self._history_tool(user_id=user_id),
            self._style_rules_tool(scene=scene),
            self._save_recommendation_tool(user_id=user_id, scene=scene),
        ]

    def _count_wardrobe_tool(self, user_id: int):
        @tool
        async def count_wardrobe_items() -> str:
            """Count total wardrobe items for a user."""
            logger.debug("Agent tool count_wardrobe_items called: user_id=%s", user_id)
            count = await self.clothes_repo.count_by_user(user_id)
            return json.dumps({"count": count}, ensure_ascii=False)

        return count_wardrobe_items

    def _get_wardrobe_items_tool(self, user_id: int):
        @tool
        async def get_wardrobe_items_by_ids(ids: list[int]) -> str:
            """Fetch full details of specific wardrobe items by their IDs."""
            logger.debug("Agent tool get_wardrobe_items_by_ids called: user_id=%s ids=%s", user_id, ids)
            items = await self.clothes_repo.get_by_ids(user_id, ids)
            payload = {
                "items": [
                    {
                        "id": item.item_id,
                        "name": item.name,
                        "category": item.category,
                        "color": item.color,
                        "seasons": item.seasons,
                        "status": item.status,
                        "image_url": item.image_url,
                        "attributes": item.attributes,
                    }
                    for item in items
                ],
                "count": len(items),
            }
            return json.dumps(payload, ensure_ascii=False)

        return get_wardrobe_items_by_ids

    def _history_tool(self, user_id: int):
        @tool
        async def get_history_recommendations(limit: int = 5) -> str:
            """Get user's past outfit recommendations."""
            logger.debug("Agent tool get_history_recommendations called: user_id=%s limit=%s", user_id, limit)
            recs = await self.recommendation_repo.list_by_user(user_id, limit=limit)
            payload = {
                "items": [
                    {
                        "recommend_id": str(rec.recommend_id),
                        "scene": rec.scene,
                        "title": rec.title,
                        "match_rate": rec.match_rate,
                        "created_at": rec.created_at.isoformat() if rec.created_at else None,
                    }
                    for rec in recs
                ],
                "count": len(recs),
            }
            return json.dumps(payload, ensure_ascii=False)

        return get_history_recommendations

    def _style_rules_tool(self, scene: str | None = None):
        @tool
        async def get_style_rules() -> str:
            """Get style rules for a given scene or general styling principles."""
            logger.debug("Agent tool get_style_rules called: scene=%s", scene)
            rules = {
                "scene": scene,
                "priority": (
                    ["根据天气", "结合衣橱可用项", "给出可执行建议"]
                    if scene is None
                    else ["天气适配", "场景一致性", "衣橱可用性"]
                ),
                "note": "优先选择用户已有衣橱中的单品进行搭配。",
            }
            return json.dumps(rules, ensure_ascii=False)

        return get_style_rules

    def _save_recommendation_tool(self, user_id: int, scene: str):
        @tool
        async def save_recommendation(
            title: str,
            description: str = "",
            reason: str = "",
            match_rate: int = 0,
            selected_item_ids: list[int] | None = None,
            weather_snapshot: dict | None = None,
        ) -> str:
            """Save an outfit recommendation to the database for history."""
            logger.debug(
                "Agent tool save_recommendation called: user_id=%s scene=%s title=%s",
                user_id,
                scene,
                title,
            )
            if selected_item_ids:
                items = await self.clothes_repo.get_by_ids(user_id, selected_item_ids)
            else:
                items = []

            rec = await self.recommendation_repo.create(
                user_id=user_id,
                scene=scene,
                title=title,
                description=description,
                reason=reason,
                match_rate=match_rate,
                weather_snapshot=weather_snapshot or {},
                items=items,
            )
            await self.session.commit()
            return json.dumps({"recommendation_id": str(rec.recommend_id)}, ensure_ascii=False)

        return save_recommendation

    # ------------------------------------------------------------------
    # Prompts
    # ------------------------------------------------------------------
    def _daily_tip_system_prompt(self) -> str:
        return (
            "你是时尚穿搭顾问 L-Wardrobe AI。你必须优先调用工具获取天气、衣橱、用户资料和规则，再输出简洁可执行的每日建议。"
            "工作流程：1) 使用 get_user_profile 获取用户位置；2) 使用 get_weather 获取天气；3) 使用 count_wardrobe_items 和 search_wardrobe 了解衣橱情况；"
            "4) 给出一条具体、可执行的建议。"
            "最终只输出严格 JSON，不要输出 markdown。字段格式："
            '{"tip": string, "weather_summary": string, "wardrobe_items_considered": number, "generated_by": string, "tool_summary": string[]}'
        )

    def _outfit_system_prompt(self) -> str:
        return (
            "你是时尚穿搭编排顾问 L-Wardrobe AI。你必须优先调用工具获取天气、衣橱、用户资料、历史推荐和规则，再生成结构化穿搭建议。"
            "工作流程：1) 使用 get_user_profile 获取用户位置；2) 使用 get_weather 获取天气；3) 使用 search_wardrobe 或 get_wardrobe_items_by_ids 查询相关单品；"
            "4) 使用 get_history_recommendations 查看历史推荐避免重复；5) 分析并推荐一套穿搭，输出 JSON。"
            "规则：- 必须从用户衣橱中选择真实存在的单品（使用 search_wardrobe 或 get_wardrobe_items_by_ids 验证）"
            "- 如果 get_user_profile 返回 digital_body_profile，必须结合身高、体重、BMI、肤色、体型、风格标签、偏好色/避雷色和版型偏好调整推荐理由"
            "- matchRate 必须是 0-100 的整数"
            "- selectedItems 必须是从衣橱中选出的真实 item_id"
            "- 如果衣橱为空或不足，如实说明并在 reason 中解释"
            "最终只输出严格 JSON，不要输出 markdown。字段格式："
            '{"name": string, "description": string, "matchRate": number, "reason": string, "image": string, "selectedItems": array, "weatherSummary": string, "toolSummary": string[], "generatedBy": string}'
        )

    def _daily_tip_user_prompt(self, user_id: int, location: str | None) -> str:
        return (
            f"用户ID: {user_id}\n"
            f"位置: {location or '深圳'}\n"
            "请产出今天的穿搭建议，语气简洁，强调可执行性。"
        )

    def _outfit_user_prompt(self, scene: str, wardrobe_ids: list[int], user_id: int, location: str | None) -> str:
        ids_str = ", ".join(map(str, wardrobe_ids)) if wardrobe_ids else "未指定"
        return (
            f"用户ID: {user_id}\n"
            f"场景: {scene}\n"
            f"可用衣橱单品ID: {ids_str}\n"
            f"位置: {location or '深圳'}\n"
            "请生成一套穿搭推荐，强调为何适合当前场景和天气。优先从可用衣橱单品中选择。"
        )

    # ------------------------------------------------------------------
    # Result normalization + fallback
    # ------------------------------------------------------------------
    def _normalize_daily_tip_result(self, result: dict, user_id: int) -> dict:
        output = self._parse_json_output(result.get("output", ""))
        tip = output.get("tip") or output.get("description") or self._default_tip({})
        return {
            "tip": tip,
            "weather_summary": output.get("weather_summary") or self._weather_summary({}),
            "wardrobe_items_considered": output.get("wardrobe_items_considered", 0),
            "generated_by": output.get("generated_by", "langchain-agent" if self._can_use_agent() else "fallback"),
            "tool_summary": output.get(
                "tool_summary", self._summarize_intermediate_steps(result.get("intermediate_steps", []))
            ),
            "raw_output": result.get("output", ""),
            "user_id": user_id,
        }

    def _normalize_outfit_result(self, result: dict, scene: str, user_id: int) -> dict:
        output = self._parse_json_output(result.get("output", ""))
        fallback = self._fallback_outfit(scene, [], {})
        merged = {**fallback, **output}
        merged.setdefault("id", str(uuid.uuid4()))
        merged.setdefault("scene", scene)
        merged.setdefault("toolSummary", self._summarize_intermediate_steps(result.get("intermediate_steps", [])))
        merged.setdefault("weatherSummary", self._weather_summary({}))
        merged.setdefault("generatedBy", "langchain-agent" if self._can_use_agent() else "fallback")
        merged.setdefault("selectedItems", [])
        merged.setdefault("raw_output", result.get("output", ""))
        merged.setdefault("user_id", user_id)
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
