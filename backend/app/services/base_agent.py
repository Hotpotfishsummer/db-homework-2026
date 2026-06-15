"""Base class for LangChain-powered agents.

The application has two LLM-driven services that share infrastructure but
diverge in business logic:

- ``StylingAgentService`` — answers "what should I wear today" using only
  items the user already owns.
- ``RecommendationAgentService`` — answers "what should I buy next" by
  combining the user's wardrobe, weather, and personal style.

Both services need the same plumbing:

1. Configure an LLM client (DeepSeek or generic OpenAI-compatible).
2. Decide whether the agent is callable (LLM key configured, deps loaded).
3. Run a LangGraph ``create_react_agent`` graph and translate its
   ``{"messages": [...]}`` result back into the v0.x AgentExecutor
   contract ``{"output": <text>, "intermediate_steps": [(action, obs), ...]}``.
4. Summarize tool invocations for logging/UI.

This module owns that plumbing. Subclasses provide the agent-specific
tools, system/user prompts, result normalization, and fallback templates.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.services.weather import WeatherService
from db.repositories.user_repo import UserRepository
from db.repositories.wardrobe_repo import ClothesRepository

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
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent

    LANGCHAIN_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    HumanMessage = None
    AIMessage = None
    ToolMessage = None
    SystemMessage = None
    tool = None
    ChatOpenAI = None
    create_react_agent = None
    LANGCHAIN_AVAILABLE = False


def _is_configured(value: str | None) -> bool:
    """Treat documented placeholders ('your_*_api_key_here') as not configured."""
    if not value:
        return False
    stripped = value.strip().lower()
    if not stripped or stripped.startswith("your_") or stripped.endswith("_here"):
        return False
    return True


class BaseAgentService:
    """Shared infrastructure for LLM-driven agents.

    Subclasses must implement (or override):
        - ``_build_*_tools(...)`` — register the tools the agent can call
        - ``_*_system_prompt()`` / ``_*_user_prompt(...)`` — prompt templates
        - ``_normalize_*_result(result, ...)`` — shape the LLM JSON into the
          service-specific response model
        - ``_fallback_*`` — deterministic response when the LLM is unavailable

    Subclasses typically also add their own constructor that calls
    ``super().__init__(session)`` then instantiates extra repositories.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.weather_service = WeatherService()
        self.clothes_repo = ClothesRepository(session)
        self.user_repo = UserRepository(session)

    # ------------------------------------------------------------------
    # Capability checks
    # ------------------------------------------------------------------
    def _can_use_agent(self) -> bool:
        has_generic = bool(
            _is_configured(settings.llm_api_key)
            and settings.llm_api_base
            and settings.llm_model
        )
        has_deepseek = _is_configured(settings.deepseek_api_key)
        return bool(LANGCHAIN_AVAILABLE and (has_generic or has_deepseek))

    # ------------------------------------------------------------------
    # LLM construction
    # ------------------------------------------------------------------
    def _build_llm(self):
        if not self._can_use_agent():
            raise RuntimeError("LangChain LLM is not available")

        if settings.deepseek_api_key and _is_configured(settings.deepseek_api_key):
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

    # ------------------------------------------------------------------
    # Agent execution
    # ------------------------------------------------------------------
    async def _run_agent(self, system_prompt: str, user_prompt: str, tools: list[Any]) -> dict[str, Any]:
        """Run the LangGraph ReAct agent and normalize the result.

        Returns the v0.x AgentExecutor contract:
        ``{"output": <final AI text>, "intermediate_steps": [(action, observation), ...]}``
        """
        logger.info(
            "Starting agent execution: tool_count=%s prompt_chars=%s",
            len(tools),
            len(user_prompt),
        )
        llm = self._build_llm()

        # The system prompt may contain JSON field-format spec like
        # `{"name": string, ...}` which would otherwise be parsed as
        # template variables if we passed a `prompt=ChatPromptTemplate(...)`
        # to langgraph. We use a callable `prompt` that returns the full
        # list of messages (system + conversation) as a plain list of
        # BaseMessage objects — langgraph passes this list to the model
        # without going through template formatting.
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
        """Convert a LangGraph message list into the v0.x ``(output, steps)`` tuple.

        Walks the message list pairing each ``AIMessage`` that has ``tool_calls``
        with the immediately following ``ToolMessage(s)``. The "output" is the
        text content of the **last** ``AIMessage`` that has no tool calls.
        """
        output = ""
        steps: list[tuple[Any, Any]] = []
        i = 0
        while i < len(messages):
            msg = messages[i]
            cls_name = type(msg).__name__
            if cls_name == "AIMessage":
                tool_calls = getattr(msg, "tool_calls", None) or []
                if tool_calls:
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
                    text = getattr(msg, "content", "") or ""
                    if text:
                        output = text
            i += 1
        return output, steps

    # ------------------------------------------------------------------
    # Common tool factories (subclasses reuse these via composition)
    # ------------------------------------------------------------------
    def _make_weather_tool(self, location: str):
        @tool
        async def get_weather(city: str | None = None) -> str:
            """Get current weather for a city. Returns temperature, condition, wind, and humidity."""
            target = city or location
            logger.debug("Agent tool get_weather called: city=%s", target)
            current = await self.weather_service.get_current(location=target)
            import json
            return json.dumps(current, ensure_ascii=False)

        return get_weather

    def _make_search_wardrobe_tool(self, user_id: int):
        @tool
        async def search_wardrobe(
            category: str = "",
            season: str = "",
            color: str = "",
            status: str = "",
            limit: int = 20,
        ) -> str:
            """Search user's wardrobe items with filters.
            category: top/bottom/outerwear/shoes/accessory/bag/other
            season: spring/summer/autumn/winter
            status: available/washing
            """
            import json
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
                    }
                    for item in items
                ],
                "count": len(items),
            }
            return json.dumps(payload, ensure_ascii=False)

        return search_wardrobe

    def _make_user_profile_tool(self, user_id: int):
        @tool
        async def get_user_profile() -> str:
            """Get user profile (display name, location, style preference)."""
            import json
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

    def _summarize_intermediate_steps(self, intermediate_steps: list[Any]) -> list[str]:
        summary: list[str] = []
        for step in intermediate_steps or []:
            try:
                action, observation = step[0], step[1]
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
