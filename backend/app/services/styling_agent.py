from __future__ import annotations

import json
import uuid
import logging
import time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.services.weather import WeatherService
from db.repositories.wardrobe_repo import ClothesRepository
from db.repositories.user_repo import UserRepository
from db.repositories.recommendation_repo import RecommendationRepository

settings = get_settings()
logger = logging.getLogger(__name__)

try:
    # langchain v1.x removed the legacy `langchain.agents.AgentExecutor` and
    # `create_tool_calling_agent` entry points. The official migration target
    # is `langgraph-prebuilt.create_react_agent`, which returns a LangGraph
    # compiled graph (compatible with `.ainvoke(...)`) backed by the same
    # tool-calling semantics. We adapt the result shape below so the rest of
    # this module keeps working with the v0.x `{"output", "intermediate_steps"}`
    # contract.
    from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent

    LANGCHAIN_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    HumanMessage = None
    AIMessage = None
    ToolMessage = None
    tool = None
    ChatOpenAI = None
    create_react_agent = None
    LANGCHAIN_AVAILABLE = False


class StylingAgentService:
    """LangChain-powered orchestration layer for wardrobe advice with dynamic database tools."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.weather_service = WeatherService()
        self.clothes_repo = ClothesRepository(session)
        self.user_repo = UserRepository(session)
        self.recommendation_repo = RecommendationRepository(session)

    async def generate_daily_tip(self, user_id: str | int | None = None, location: str | None = None) -> dict:
        started_at = time.perf_counter()
        resolved_user_id = int(user_id) if user_id is not None else 0
        resolved_location = location or "深圳"
        logger.info("Daily tip generation started: user_id=%s location=%s", resolved_user_id, resolved_location)

        if not self._can_use_agent():
            logger.warning("Daily tip generation falling back because agent is unavailable")
            weather = await self.weather_service.get_current(location=resolved_location)
            return self._fallback_daily_tip(weather, [])

        tools = self._build_daily_tip_tools(resolved_user_id, resolved_location)
        logger.info("Daily tip agent tools prepared: tool_count=%s", len(tools))

        result = await self._run_agent(
            system_prompt=self._daily_tip_system_prompt(),
            user_prompt=self._daily_tip_user_prompt(user_id=resolved_user_id, location=resolved_location),
            tools=tools,
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
    ) -> dict:
        started_at = time.perf_counter()
        resolved_user_id = int(user_id) if user_id is not None else 0
        resolved_location = location or "深圳"
        logger.info(
            "Outfit recommendation started: scene=%s wardrobe_count=%s user_id=%s location=%s",
            scene,
            len(wardrobe_ids or []),
            resolved_user_id,
            resolved_location,
        )

        if not self._can_use_agent():
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
        )
        normalized = self._normalize_outfit_result(result, scene=scene, user_id=resolved_user_id)
        logger.info(
            "Outfit recommendation finished: generated_by=%s matchRate=%s elapsed_ms=%.2f",
            normalized.get("generatedBy"),
            normalized.get("matchRate"),
            (time.perf_counter() - started_at) * 1000,
        )
        return normalized

    def _can_use_agent(self) -> bool:
        # Treat the documented "your_*_api_key_here" placeholders as
        # "not configured" so the agent doesn't try to call an LLM endpoint
        # with a literal placeholder key (which yields a 401 mid-run).
        def _is_configured(value: str | None) -> bool:
            if not value:
                return False
            stripped = value.strip().lower()
            if not stripped or stripped.startswith("your_") or stripped.endswith("_here"):
                return False
            return True

        has_generic = bool(
            _is_configured(settings.llm_api_key)
            and settings.llm_api_base
            and settings.llm_model
        )
        has_deepseek = _is_configured(settings.deepseek_api_key)
        return bool(LANGCHAIN_AVAILABLE and (has_generic or has_deepseek))

    def _build_llm(self):
        if not self._can_use_agent():
            raise RuntimeError("LangChain LLM is not available")

        if settings.deepseek_api_key and settings.deepseek_api_key.strip() and not settings.deepseek_api_key.strip().lower().startswith("your_"):
            api_key = settings.deepseek_api_key
            base_url = settings.deepseek_base_url
            model = settings.llm_model or "deepseek-chat"
            logger.debug("Using DeepSeek LLM: base_url=%s model=%s", base_url, model)
        else:
            api_key = settings.llm_api_key
            base_url = settings.llm_api_base
            model = settings.llm_model
            logger.debug("Using generic OpenAI-compatible LLM: base_url=%s model=%s", base_url, model)

        return ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

    async def _run_agent(self, system_prompt: str, user_prompt: str, tools: list[Any]) -> dict[str, Any]:
        """Run the LangGraph ReAct agent and normalize the result.

        langgraph's `create_react_agent` returns a compiled graph whose
        `.ainvoke(...)` yields `{"messages": [HumanMessage, AIMessage(...),
        ToolMessage(...), AIMessage(...), ...]}`. To keep the rest of this
        module (the `_normalize_*_result` helpers and downstream callers)
        unchanged, we reshape the graph result into the v0.x AgentExecutor
        contract: `{"output": <final AI text>, "intermediate_steps":
        [(action, observation), ...]}`.
        """
        logger.info("Starting agent execution: tool_count=%s prompt_chars=%s", len(tools), len(user_prompt))
        llm = self._build_llm()

        # The system prompt contains a JSON field-format spec like
        # `{"name": string, ...}` which would otherwise be parsed as
        # template variables if we passed a `prompt=ChatPromptTemplate(...)`
        # to langgraph. To avoid that, we use a callable `prompt` that
        # returns the full list of messages (system + conversation) as a
        # plain list of BaseMessage objects — langgraph will pass this list
        # to the model without going through template formatting.
        from langchain_core.messages import SystemMessage

        def _prompt_callable(state: dict) -> list[Any]:
            return [SystemMessage(content=system_prompt), *state.get("messages", [])]

        graph = create_react_agent(
            llm,
            tools,
            prompt=_prompt_callable,
        )

        started_at = time.perf_counter()
        result = await graph.ainvoke(
            {"messages": [HumanMessage(content=user_prompt)]},
            config={"recursion_limit": max(4, settings.agent_max_iterations * 2 + 2)},
        )
        raw_messages = result.get("messages", []) or []
        output, intermediate_steps = self._extract_output_and_steps(raw_messages)
        logger.info(
            "Agent execution finished: output_chars=%s intermediate_steps=%s elapsed_ms=%.2f",
            len(str(output)),
            len(intermediate_steps),
            (time.perf_counter() - started_at) * 1000,
        )
        logger.debug("Agent raw result keys: %s", sorted(result.keys()))
        return {"output": output, "intermediate_steps": intermediate_steps}

    @staticmethod
    def _extract_output_and_steps(messages: list[Any]) -> tuple[str, list[tuple[Any, Any]]]:
        """Convert a LangGraph message list into the v0.x `(output, steps)` tuple.

        Walks the message list pairing each `AIMessage` that has `tool_calls`
        with the immediately following `ToolMessage(s)`. The "output" is the
        text content of the **last** `AIMessage` that has no tool calls (i.e.
        the final answer the agent emitted).
        """
        output = ""
        steps: list[tuple[Any, Any]] = []
        i = 0
        while i < len(messages):
            msg = messages[i]
            cls_name = type(msg).__name__
            if cls_name == "AIMessage":
                # Collect any tool_calls on this AIMessage.
                tool_calls = getattr(msg, "tool_calls", None) or []
                if tool_calls:
                    # Pair each tool_call with the next ToolMessage sharing
                    # the same tool_call_id (the graph emits one ToolMessage
                    # per tool call).
                    pending = {tc["id"]: tc for tc in tool_calls if isinstance(tc, dict) and "id" in tc}
                    j = i + 1
                    while j < len(messages) and pending:
                        nxt = messages[j]
                        if type(nxt).__name__ != "ToolMessage":
                            j += 1
                            continue
                        tc_id = getattr(nxt, "tool_call_id", None)
                        action = pending.pop(tc_id, None)
                        if action is not None:
                            steps.append((action, getattr(nxt, "content", "")))
                        j += 1
                else:
                    # No tool calls → this is the final answer (or an interim
                    # text-only message; we keep the latest one as `output`).
                    text = getattr(msg, "content", "") or ""
                    if text:
                        output = text
            i += 1
        return output, steps

    def _build_daily_tip_tools(
        self,
        user_id: int,
        location: str,
    ) -> list[Any]:
        if not LANGCHAIN_AVAILABLE:
            return []

        return [
            self._weather_tool(location=location),
            self._search_wardrobe_tool(user_id=user_id),
            self._count_wardrobe_tool(user_id=user_id),
            self._get_wardrobe_items_tool(user_id=user_id),
            self._user_profile_tool(user_id=user_id),
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
            self._weather_tool(location=location),
            self._search_wardrobe_tool(user_id=user_id),
            self._get_wardrobe_items_tool(user_id=user_id),
            self._count_wardrobe_tool(user_id=user_id),
            self._user_profile_tool(user_id=user_id),
            self._history_tool(user_id=user_id),
            self._style_rules_tool(scene=scene),
            self._save_recommendation_tool(user_id=user_id, scene=scene),
        ]

    def _weather_tool(self, location: str):
        @tool
        async def get_weather(city: str | None = None) -> str:
            """Get current weather for a city. Returns temperature, condition, wind, and humidity."""
            target = city or location
            logger.debug("Agent tool get_weather called: city=%s", target)
            current = await self.weather_service.get_current(location=target)
            return json.dumps(current, ensure_ascii=False)

        return get_weather

    def _search_wardrobe_tool(self, user_id: int):
        @tool
        async def search_wardrobe(
            category: str = "",
            season: str = "",
            color: str = "",
            status: str = "",
            limit: int = 20,
        ) -> str:
            """Search user's wardrobe items with filters. Use to find relevant clothes for an outfit.
            Category can be: top, bottom, outerwear, shoes, accessory, bag, other.
            Season can be: spring, summer, autumn, winter.
            Status can be: available, washing.
            """
            logger.debug(
                "Agent tool search_wardrobe called: user_id=%s category=%s season=%s color=%s status=%s limit=%s",
                user_id,
                category,
                season,
                color,
                status,
                limit,
            )
            items = await self.clothes_repo.list_by_user(
                user_id,
                category=category or None,
                season=season or None,
                color=color or None,
                status=status or None,
                limit=limit,
                offset=0,
            )
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

        return search_wardrobe

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

    def _count_wardrobe_tool(self, user_id: int):
        @tool
        async def count_wardrobe_items() -> str:
            """Count total wardrobe items for a user."""
            logger.debug("Agent tool count_wardrobe_items called: user_id=%s", user_id)
            count = await self.clothes_repo.count_by_user(user_id)
            return json.dumps({"count": count}, ensure_ascii=False)

        return count_wardrobe_items

    def _user_profile_tool(self, user_id: int):
        @tool
        async def get_user_profile() -> str:
            """Get user profile including display name, location, and style preference."""
            logger.debug("Agent tool get_user_profile called: user_id=%s", user_id)
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return json.dumps({"error": "User not found"}, ensure_ascii=False)
            profile = {
                "user_id": user.user_id,
                "username": user.username,
                "display_name": user.display_name,
                "style_preference": user.style_preference,
                "location": user.location,
            }
            return json.dumps(profile, ensure_ascii=False)

        return get_user_profile

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

    def _summarize_intermediate_steps(self, intermediate_steps: list[Any]) -> list[str]:
        summary: list[str] = []
        for step in intermediate_steps or []:
            try:
                action, observation = step[0], step[1]
                # After the langgraph migration `action` is a dict (the
                # tool_call payload) instead of an AgentAction object. Handle
                # both shapes so the log output stays stable.
                if isinstance(action, dict):
                    tool_name = action.get("name") or action.get("tool") or "tool"
                else:
                    tool_name = (
                        getattr(action, "tool", None)
                        or getattr(action, "tool_name", None)
                        or "tool"
                    )
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
