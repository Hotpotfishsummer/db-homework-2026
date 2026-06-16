"""AI recommendation agent (推荐新购单品 + 嵌入搭配 + 衣橱缺口分析).

Distinct from ``StylingAgentService`` (衣橱内组合) — this service answers
"what should I buy next" by combining the user's wardrobe, weather, and
style preference. It can:

- ``recommend_items`` — recommend 5-8 *new* items for the user to buy
- ``recommend_with_wardrobe`` — produce a full outfit where each slot is
  marked ``need_buy: true/false`` to mix owned and recommended items
- ``analyze_wardrobe_gap`` — return a structured report of category-level
  gaps in the wardrobe

Inherits LLM/agent plumbing from ``BaseAgentService``. Adds one
recommendation-specific tool, ``analyze_wardrobe_gap``, which the LLM
can call inside the ReAct loop.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections import Counter
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base_agent import (
    BaseAgentService,
    LANGCHAIN_AVAILABLE,
    tool,
)
from app.core.user_llm import UserLLMConfig
from db.repositories.shopping_recommendation_repo import ShoppingRecommendationRepository

logger = logging.getLogger(__name__)


# Category-level target counts used by the wardrobe gap analyzer. These are
# a rough heuristic, not a hard rule. Tunable via env / config later.
_GAP_TARGETS = {
    "top": 5,
    "bottom": 4,
    "outerwear": 2,
    "shoes": 3,
    "accessory": 3,
    "bag": 1,
    "other": 2,
}


class RecommendationAgentService(BaseAgentService):
    """LangChain-powered AI recommendation service (新购 + 嵌入 + 缺口)."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.shopping_repo = ShoppingRecommendationRepository(session)

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------
    async def recommend_items(
        self,
        scene: str,
        user_id: str | int | None = None,
        location: str | None = None,
        gap_focus: str | None = None,
        user_llm: UserLLMConfig | None = None,
    ) -> dict:
        started_at = time.perf_counter()
        resolved_user_id = int(user_id) if user_id is not None else 0
        resolved_location = location or "深圳"
        logger.info(
            "Items recommendation started: scene=%s gap_focus=%s user_id=%s location=%s",
            scene, gap_focus, resolved_user_id, resolved_location,
        )

        if not self._can_use_agent(user_llm=user_llm):
            logger.warning("Items recommendation falling back because agent is unavailable")
            return self._fallback_items(scene, gap_focus)

        tools = self._build_recommendation_tools(resolved_user_id, resolved_location)
        logger.info("Items recommendation agent tools prepared: tool_count=%s", len(tools))

        result = await self._run_agent(
            system_prompt=self._items_system_prompt(),
            user_prompt=self._items_user_prompt(
                scene=scene, user_id=resolved_user_id, location=resolved_location, gap_focus=gap_focus,
            ),
            tools=tools,
            user_llm=user_llm,
        )
        normalized = self._normalize_items_result(
            result, scene=scene, user_id=resolved_user_id, location=resolved_location,
        )

        # Persist each recommended item to the shopping_recommendations table
        # with status=pending. We do this *after* normalization so any fallback
        # path also writes a row (still useful for the user to track).
        items_to_persist = normalized.get("items", [])
        if items_to_persist:
            try:
                await self.shopping_repo.create_batch(
                    resolved_user_id,
                    items_to_persist,
                    scene=scene,
                    weather_snapshot={"summary": normalized.get("weatherSummary")},
                )
                await self.session.commit()
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Persisting shopping items failed: %s", exc)
                await self.session.rollback()

        logger.info(
            "Items recommendation finished: item_count=%s elapsed_ms=%.2f",
            len(items_to_persist), (time.perf_counter() - started_at) * 1000,
        )
        return normalized

    async def recommend_with_wardrobe(
        self,
        scene: str,
        user_id: str | int | None = None,
        location: str | None = None,
        user_llm: UserLLMConfig | None = None,
    ) -> dict:
        started_at = time.perf_counter()
        resolved_user_id = int(user_id) if user_id is not None else 0
        resolved_location = location or "深圳"
        logger.info(
            "Shopping-outfit started: scene=%s user_id=%s location=%s",
            scene, resolved_user_id, resolved_location,
        )

        if not self._can_use_agent(user_llm=user_llm):
            logger.warning("Shopping-outfit falling back because agent is unavailable")
            return self._fallback_shopping_outfit(scene)

        tools = self._build_recommendation_tools(resolved_user_id, resolved_location)
        result = await self._run_agent(
            system_prompt=self._shopping_outfit_system_prompt(),
            user_prompt=self._shopping_outfit_user_prompt(
                scene=scene, user_id=resolved_user_id, location=resolved_location,
            ),
            tools=tools,
            user_llm=user_llm,
        )
        normalized = self._normalize_shopping_outfit_result(
            result, scene=scene, user_id=resolved_user_id, location=resolved_location,
        )
        logger.info(
            "Shopping-outfit finished: slot_count=%s elapsed_ms=%.2f",
            len(normalized.get("outfit", {}).get("slots", [])),
            (time.perf_counter() - started_at) * 1000,
        )
        return normalized

    async def analyze_wardrobe_gap(
        self,
        user_id: str | int | None = None,
        location: str | None = None,
        user_llm: UserLLMConfig | None = None,
    ) -> dict:
        started_at = time.perf_counter()
        resolved_user_id = int(user_id) if user_id is not None else 0
        resolved_location = location or "深圳"
        logger.info(
            "Gap analysis started: user_id=%s location=%s", resolved_user_id, resolved_location,
        )

        # Step 1: pull aggregate stats directly from DB (deterministic, no LLM).
        gap_data = await self._compute_wardrobe_gap(resolved_user_id)

        # Step 2: if LLM available, polish the report with natural-language
        # summary + per-category advice. Otherwise return a deterministic
        # fallback that the frontend can render.
        if not self._can_use_agent(user_llm=user_llm):
            logger.warning("Gap analysis falling back because agent is unavailable")
            return self._fallback_gap_report(gap_data, resolved_user_id)

        tools = self._build_recommendation_tools(resolved_user_id, resolved_location)
        result = await self._run_agent(
            system_prompt=self._gap_system_prompt(),
            user_prompt=self._gap_user_prompt(user_id=resolved_user_id, gap_data=gap_data),
            tools=tools,
            user_llm=user_llm,
        )
        normalized = self._normalize_gap_result(result, gap_data, resolved_user_id)
        logger.info(
            "Gap analysis finished: gap_count=%s elapsed_ms=%.2f",
            len(normalized.get("report", {}).get("gaps", [])),
            (time.perf_counter() - started_at) * 1000,
        )
        return normalized

    # ------------------------------------------------------------------
    # Tool builders
    # ------------------------------------------------------------------
    def _build_recommendation_tools(self, user_id: int, location: str) -> list[Any]:
        if not LANGCHAIN_AVAILABLE:
            return []
        return [
            self._make_weather_tool(location=location),
            self._make_search_wardrobe_tool(user_id=user_id),
            self._count_wardrobe_tool(user_id=user_id),
            self._make_user_profile_tool(user_id=user_id),
            self._wardrobe_gap_tool(user_id=user_id),
        ]

    def _count_wardrobe_tool(self, user_id: int):
        @tool
        async def count_wardrobe_items() -> str:
            """Count total wardrobe items for a user."""
            logger.debug("Agent tool count_wardrobe_items called: user_id=%s", user_id)
            count = await self.clothes_repo.count_by_user(user_id)
            return json.dumps({"count": count}, ensure_ascii=False)

        return count_wardrobe_items

    def _wardrobe_gap_tool(self, user_id: int):
        @tool
        async def analyze_wardrobe_gap() -> str:
            """Compute category-level wardrobe gap statistics.
            Returns per-category current count, suggested target, and a
            'gap' flag indicating whether the user is short on that category.
            Use this before recommending items to know which categories to
            focus on.
            """
            logger.debug("Agent tool analyze_wardrobe_gap called: user_id=%s", user_id)
            data = await self._compute_wardrobe_gap(user_id)
            return json.dumps(data, ensure_ascii=False)

        return analyze_wardrobe_gap

    async def _compute_wardrobe_gap(self, user_id: int) -> dict:
        """Deterministic per-category wardrobe statistics."""
        items = await self.clothes_repo.list_by_user(user_id, limit=500, offset=0)
        counts = Counter(item.category for item in items)
        # dominant color
        color_counter = Counter(
            (item.color or "未知").lower() for item in items if item.color
        )
        categories = []
        for cat, target in _GAP_TARGETS.items():
            current = counts.get(cat, 0)
            gap = max(0, target - current)
            categories.append(
                {
                    "category": cat,
                    "current": current,
                    "target": target,
                    "gap": gap,
                    "is_short": gap > 0,
                }
            )
        return {
            "total": sum(counts.values()),
            "per_category": categories,
            "dominant_colors": [
                {"color": color, "count": cnt}
                for color, cnt in color_counter.most_common(3)
            ],
        }

    # ------------------------------------------------------------------
    # Prompts
    # ------------------------------------------------------------------
    def _items_system_prompt(self) -> str:
        return (
            "你是时尚穿搭推荐顾问 L-Wardrobe AI。专门为用户推荐**新购**的衣物单品(用户当前衣橱还没有的)。"
            "你必须优先调用工具获取天气、用户资料、衣橱现状和缺口分析,再生成结构化建议。"
            "工作流程:1) 使用 get_user_profile 获取用户风格偏好和位置;2) 使用 get_weather 获取天气;"
            "3) 使用 analyze_wardrobe_gap 了解衣橱分类缺口;4) 使用 count_wardrobe_items / search_wardrobe 查重和风格对齐;"
            "5) 推荐 5-8 件新单品,每件给出名称/分类/颜色/风格标签/价格区间/推荐理由/优先级。"
            "规则:- 推荐的单品必须不在用户现有衣橱中(用 search_wardrobe 验证不重复)"
            "- category 必须是: top / bottom / outerwear / shoes / accessory / bag / other"
            "- price_range 推荐用区间格式如 '100-300元'"
            "- reason 要结合用户当前衣橱缺口(用 analyze_wardrobe_gap 结果)和天气"
            "- priority 是 0-100 的整数,越高越推荐先买"
            "最终只输出严格 JSON,不要输出 markdown。字段格式:"
            '{"items": [{"name": string, "category": string, "color": string, "style_tags": string[], '
            '"price_range": string, "reason": string, "priority": number}], '
            '"weatherSummary": string, "generatedBy": string}'
        )

    def _items_user_prompt(self, scene: str, user_id: int, location: str | None, gap_focus: str | None) -> str:
        focus = f"\n重点关注品类: {gap_focus}" if gap_focus else ""
        return (
            f"用户ID: {user_id}\n"
            f"场景: {scene}\n"
            f"位置: {location or '深圳'}"
            f"{focus}\n"
            f"请基于用户的风格偏好、当前天气、衣橱缺口,推荐 5-8 件值得新购的衣物单品。"
        )

    def _shopping_outfit_system_prompt(self) -> str:
        return (
            "你是时尚穿搭编排顾问 L-Wardrobe AI。专门为用户编排一套**混合**穿搭方案:"
            "尽量复用用户已有衣橱,如果某 slot 用户没有合适单品,推荐新购。"
            "工作流程:1) 使用 get_user_profile 获取用户风格偏好和位置;2) 使用 get_weather 获取天气;"
            "3) 使用 analyze_wardrobe_gap 了解衣橱缺口;4) 使用 search_wardrobe 查询可用的衣橱单品;"
            "5) 输出 4-5 个 slot 的完整搭配,每个 slot 标记 need_buy 表示是否需要新购。"
            "规则:- 至少 1 个 slot 的 need_buy=true(否则不算 AI 推荐)"
            "- need_buy=false 的 slot 必须给出 wardrobe_id(衣橱单品 id)和 image"
            "- need_buy=true 的 slot 不需要 wardrobe_id,给出 name/reason 即可"
            "- matchRate 必须是 0-100 的整数"
            "最终只输出严格 JSON,不要输出 markdown。字段格式:"
            '{"outfit": {"name": string, "description": string, "matchRate": number, '
            '"slots": [{"category": string, "name": string, "need_buy": boolean, '
            '"wardrobe_id": number|null, "image": string|null, "reason": string}]}, '
            '"weatherSummary": string, "generatedBy": string}'
        )

    def _shopping_outfit_user_prompt(self, scene: str, user_id: int, location: str | None) -> str:
        return (
            f"用户ID: {user_id}\n"
            f"场景: {scene}\n"
            f"位置: {location or '深圳'}\n"
            "请基于用户的衣橱现状和天气,推荐一套混合搭配(衣橱单品 + 新购单品)。"
        )

    def _gap_system_prompt(self) -> str:
        return (
            "你是衣橱诊断顾问 L-Wardrobe AI。基于已经为你计算好的衣橱分类统计,给出自然语言的诊断报告。"
            "工作流程:1) 阅读 user_prompt 中已经准备好的 gap_data;2) 输出 1 段总结 + 每缺一个 category 给一条具体建议。"
            "规则:- summary 控制在 50-80 字,语气温和实用"
            "- 每个 gap item 的 advice 控制在 20-40 字,具体到品类/颜色/价位"
            "- 不要重复 user_prompt 中已有的统计数据,只补充自然语言解读"
            "最终只输出严格 JSON,不要输出 markdown。字段格式:"
            '{"summary": string, "advice_overrides": [{"category": string, "advice": string}]}'
        )

    def _gap_user_prompt(self, user_id: int, gap_data: dict) -> str:
        return (
            f"用户ID: {user_id}\n"
            f"衣橱统计已计算好,直接基于以下数据给出诊断报告:\n"
            f"{json.dumps(gap_data, ensure_ascii=False)}\n"
            "请输出 summary (50-80 字) 和 advice_overrides (仅覆盖真正缺/过剩的 category)。"
        )

    # ------------------------------------------------------------------
    # Result normalization + fallback
    # ------------------------------------------------------------------
    def _normalize_items_result(
        self, result: dict, scene: str, user_id: int, location: str,
    ) -> dict:
        output = self._parse_json_output(result.get("output", ""))
        items = output.get("items", [])
        if not isinstance(items, list):
            items = []
        # Coerce / sanitize each item
        sanitized: list[dict] = []
        for raw in items:
            if not isinstance(raw, dict):
                continue
            item = {
                "name": str(raw.get("name", "推荐单品")).strip()[:150],
                "category": self._coerce_category(raw.get("category")),
                "color": raw.get("color"),
                "style_tags": list(raw.get("style_tags") or [])[:10],
                "price_range": raw.get("price_range"),
                "purchase_url": raw.get("purchase_url"),
                "reason": str(raw.get("reason", "")).strip(),
                "priority": self._coerce_priority(raw.get("priority")),
            }
            sanitized.append(item)
        return {
            "items": sanitized,
            "scene": scene,
            "weatherSummary": output.get("weatherSummary") or self._weather_summary({}),
            "toolSummary": self._summarize_intermediate_steps(result.get("intermediate_steps", [])),
            "generatedBy": "langchain-agent" if self._can_use_agent() else "fallback",
            "raw_output": result.get("output", ""),
            "user_id": user_id,
        }

    def _normalize_shopping_outfit_result(
        self, result: dict, scene: str, user_id: int, location: str,
    ) -> dict:
        output = self._parse_json_output(result.get("output", ""))
        outfit = output.get("outfit", {}) if isinstance(output, dict) else {}
        if not isinstance(outfit, dict):
            outfit = {}
        slots = outfit.get("slots", [])
        if not isinstance(slots, list):
            slots = []
        sanitized_slots: list[dict] = []
        for raw in slots:
            if not isinstance(raw, dict):
                continue
            need_buy = bool(raw.get("need_buy", False))
            ward_id = raw.get("wardrobe_id")
            try:
                ward_id_int = int(ward_id) if ward_id is not None else None
            except (TypeError, ValueError):
                ward_id_int = None
            slot = {
                "category": self._coerce_category(raw.get("category")),
                "name": str(raw.get("name", "未命名")).strip()[:150],
                "need_buy": need_buy,
                "wardrobe_id": ward_id_int,
                "image": raw.get("image") if not need_buy else None,
                "reason": str(raw.get("reason", "")).strip(),
            }
            sanitized_slots.append(slot)
        # Coerce matchRate
        try:
            match_rate = int(outfit.get("matchRate", 80))
        except (TypeError, ValueError):
            match_rate = 80
        match_rate = max(0, min(100, match_rate))
        return {
            "outfit": {
                "id": outfit.get("id") or str(uuid.uuid4()),
                "name": str(outfit.get("name", f"{scene}风格混合搭配")).strip(),
                "description": str(outfit.get("description", "")).strip(),
                "matchRate": match_rate,
                "scene": scene,
                "slots": sanitized_slots,
            },
            "weatherSummary": output.get("weatherSummary") or self._weather_summary({}),
            "toolSummary": self._summarize_intermediate_steps(result.get("intermediate_steps", [])),
            "generatedBy": "langchain-agent" if self._can_use_agent() else "fallback",
            "raw_output": result.get("output", ""),
            "user_id": user_id,
        }

    def _normalize_gap_result(
        self, result: dict, gap_data: dict, user_id: int,
    ) -> dict:
        output = self._parse_json_output(result.get("output", ""))
        # Build the gaps list from gap_data, optionally overriding advice
        # with LLM-suggested per-category strings.
        overrides = {
            item.get("category"): item.get("advice")
            for item in (output.get("advice_overrides") or [])
            if isinstance(item, dict) and item.get("category")
        }
        gaps = []
        for cat in gap_data.get("per_category", []):
            advice = overrides.get(cat["category"])
            if not advice:
                if cat["is_short"]:
                    advice = f"建议补 {cat['gap']} 件 {cat['category']} 类单品"
                else:
                    advice = f"{cat['category']} 类数量充足,无需补充"
            gaps.append(
                {
                    "category": cat["category"],
                    "current": cat["current"],
                    "suggested": cat["target"],
                    "advice": advice,
                }
            )
        summary = output.get("summary") or "衣橱整体分布如上,优先补充标注为缺口的品类。"
        return {
            "report": {
                "summary": str(summary).strip(),
                "gaps": gaps,
                "total_items": gap_data.get("total", 0),
                "dominant_colors": gap_data.get("dominant_colors", []),
                "generatedBy": "langchain-agent" if self._can_use_agent() else "fallback",
            },
            "toolSummary": self._summarize_intermediate_steps(result.get("intermediate_steps", [])),
            "raw_output": result.get("output", ""),
            "user_id": user_id,
        }

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

    @staticmethod
    def _coerce_category(value: Any) -> str:
        if not value:
            return "other"
        v = str(value).strip().lower()
        allowed = {"top", "bottom", "outerwear", "shoes", "accessory", "bag", "other"}
        return v if v in allowed else "other"

    @staticmethod
    def _coerce_priority(value: Any) -> int:
        try:
            p = int(value) if value is not None else 50
        except (TypeError, ValueError):
            return 50
        return max(0, min(100, p))

    # ------------------------------------------------------------------
    # Fallback templates (deterministic, no LLM)
    # ------------------------------------------------------------------
    def _fallback_items(self, scene: str, gap_focus: str | None) -> dict:
        return {
            "items": [],
            "scene": scene,
            "weatherSummary": self._weather_summary({}),
            "toolSummary": ["agent unavailable: please configure LLM_API_KEY"],
            "generatedBy": "fallback",
            "raw_output": "",
            "user_id": 0,
        }

    def _fallback_shopping_outfit(self, scene: str) -> dict:
        return {
            "outfit": {
                "id": str(uuid.uuid4()),
                "name": f"{scene}混合搭配 (降级)",
                "description": "AI 服务暂不可用,降级返回空方案",
                "matchRate": 0,
                "scene": scene,
                "slots": [],
            },
            "weatherSummary": self._weather_summary({}),
            "toolSummary": ["agent unavailable: please configure LLM_API_KEY"],
            "generatedBy": "fallback",
            "raw_output": "",
            "user_id": 0,
        }

    def _fallback_gap_report(self, gap_data: dict, user_id: int) -> dict:
        gaps = []
        for cat in gap_data.get("per_category", []):
            if cat["is_short"]:
                advice = f"建议补 {cat['gap']} 件 {cat['category']} 类单品"
            else:
                advice = f"{cat['category']} 类数量充足"
            gaps.append(
                {
                    "category": cat["category"],
                    "current": cat["current"],
                    "suggested": cat["target"],
                    "advice": advice,
                }
            )
        short = [g["category"] for g in gaps if g["current"] < g["suggested"]]
        summary = (
            f"衣橱共 {gap_data.get('total', 0)} 件,缺: {', '.join(short) if short else '无'}"
        )
        return {
            "report": {
                "summary": summary,
                "gaps": gaps,
                "total_items": gap_data.get("total", 0),
                "dominant_colors": gap_data.get("dominant_colors", []),
                "generatedBy": "fallback",
            },
            "toolSummary": ["deterministic gap computation (no LLM)"],
            "raw_output": "",
            "user_id": user_id,
        }
