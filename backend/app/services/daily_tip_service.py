"""Static daily styling knowledge tips for the popup entry point."""

from __future__ import annotations

import json
from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from db.models.daily_tip import DailyTip
from db.repositories.daily_tip_repo import DailyTipRepository

STORAGE_TIP_TYPE = "outfit"

STATIC_TIPS: list[dict[str, Any]] = [
    {
        "tip_type": "color",
        "title": "三色原则降低搭配出错率",
        "content": "全身主色控制在三种以内，会让视觉更干净。新手可以先固定一个基础色，再用一个低饱和颜色制造层次。",
        "example": "白色上衣 + 深蓝下装 + 黑色鞋包",
        "tags": ["配色", "基础法则", "通勤"],
    },
    {
        "tip_type": "silhouette",
        "title": "上短下长更容易优化比例",
        "content": "当上衣下摆停在腰线附近，下装保持纵向延伸时，整体重心会被抬高，看起来更利落。",
        "example": "短款针织衫 + 高腰直筒裤",
        "tags": ["比例", "版型", "显高"],
    },
    {
        "tip_type": "fabric",
        "title": "同色不同材质能做出层次",
        "content": "颜色接近时，可以靠面料差异避免单调。棉、针织、皮革或缎面混搭，会比单纯堆颜色更稳。",
        "example": "米白棉 T + 米色针织外套 + 浅卡其裤",
        "tags": ["面料", "层次", "质感"],
    },
    {
        "tip_type": "occasion",
        "title": "正式感来自线条和干净度",
        "content": "通勤穿搭不一定要复杂。挺括线条、干净鞋面和少量配饰，通常比大量设计元素更显得体。",
        "example": "衬衫 + 直筒裤 + 简洁乐福鞋",
        "tags": ["通勤", "场景", "得体"],
    },
    {
        "tip_type": "body_shape",
        "title": "露出最细的位置更显轻盈",
        "content": "手腕、脚踝和腰线通常是视觉上更利落的位置。适当露出或强调这些位置，可以减少臃肿感。",
        "example": "九分直筒裤 + 低帮鞋",
        "tags": ["显瘦", "比例", "细节"],
    },
    {
        "tip_type": "color",
        "title": "上下呼应能提升完整度",
        "content": "鞋、包、腰带或帽子里有一个颜色与上衣呼应，整体会更像一套搭配，而不是临时拼在一起。",
        "example": "蓝色衬衫 + 蓝色包饰 + 中性色下装",
        "tags": ["配色", "呼应", "完整度"],
    },
    {
        "tip_type": "wardrobe",
        "title": "基础款决定衣橱利用率",
        "content": "一件衣服能不能常穿，关键看它能否和三件以上已有单品组合。购买或保留前，可以先做这个判断。",
        "example": "白衬衫可搭牛仔裤、西裤、半裙",
        "tags": ["衣橱", "基础款", "复穿"],
    },
    {
        "tip_type": "silhouette",
        "title": "宽松单品需要一个收束点",
        "content": "如果上衣和下装都偏宽松，最好用腰线、袖口、裤脚或鞋型制造收束，否则容易显得没精神。",
        "example": "宽松卫衣 + 直筒裤 + 利落鞋型",
        "tags": ["版型", "松紧", "休闲"],
    },
    {
        "tip_type": "care",
        "title": "针织单品少挂多叠",
        "content": "厚针织长期悬挂容易被拉长变形。清洗晾干后平叠收纳，更能保持肩线和衣身形状。",
        "example": "毛衣、针织开衫平叠放置",
        "tags": ["护理", "针织", "收纳"],
    },
    {
        "tip_type": "fabric",
        "title": "挺括面料更容易显精神",
        "content": "当你想让造型更利落时，优先选择有支撑感的面料。过软的材质虽然舒适，但更依赖身形和搭配层次。",
        "example": "挺括衬衫 + 直筒裤",
        "tags": ["面料", "精神感", "通勤"],
    },
]


class DailyTipService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.tip_repo = DailyTipRepository(session)

    async def get_today_tip(self, *, user_id: int) -> dict[str, Any]:
        existing = await self.tip_repo.get_today(user_id, tip_type=STORAGE_TIP_TYPE)
        if existing is not None:
            return self._serialize_tip(existing, viewed_today=True)

        payload = self._pick_static_tip(user_id=user_id)
        record = await self.tip_repo.create_or_get(
            user_id,
            content=json.dumps(payload, ensure_ascii=False),
            tip_type=STORAGE_TIP_TYPE,
        )
        await self.session.commit()
        return self._serialize_tip(record, viewed_today=False)

    def _pick_static_tip(self, *, user_id: int) -> dict[str, Any]:
        index = (date.today().toordinal() + user_id) % len(STATIC_TIPS)
        payload = dict(STATIC_TIPS[index])
        payload["generated_by"] = "static"
        return payload

    def _serialize_tip(self, tip: DailyTip, *, viewed_today: bool) -> dict[str, Any]:
        try:
            payload = json.loads(tip.content)
            if not isinstance(payload, dict):
                payload = {}
        except json.JSONDecodeError:
            payload = {"content": tip.content}

        return {
            "tip_id": tip.tip_id,
            "tip_date": tip.tip_date.isoformat() if tip.tip_date else None,
            "tip_type": str(payload.get("tip_type") or "color"),
            "title": str(payload.get("title") or "今日穿搭小知识"),
            "content": str(payload.get("content") or payload.get("tip") or tip.content),
            "example": payload.get("example"),
            "tags": payload.get("tags") if isinstance(payload.get("tags"), list) else [],
            "generated_by": str(payload.get("generated_by") or "static"),
            "viewed_today": viewed_today,
            "created_at": tip.created_at,
        }
