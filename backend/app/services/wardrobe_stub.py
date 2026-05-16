class WardrobeService:
    """
    衣橱数据查询接口。当前为 stub 实现，返回 mock 数据。
    TODO: 接入真实数据库时，替换为 SQLAlchemy 或 ORM 查询。
    """

    async def get_by_ids(self, user_id: str, ids: list[int]) -> list[dict]:
        """根据 wardrobeIds 查询衣服详情。当前返回固定 mock 数据。"""
        # STUB: 返回一组 demo 衣服用于 AI prompt
        return [
            {"id": 1, "name": "白色衬衫", "category": "上装", "color": "#FFFFFF"},
            {"id": 2, "name": "黑色休闲裤", "category": "下装", "color": "#1a1a1a"},
            {"id": 3, "name": "灰色卫衣", "category": "上装", "color": "#9ca3af"},
            {"id": 4, "name": "白色运动鞋", "category": "鞋靴", "color": "#FFFFFF"},
            {"id": 5, "name": "蓝色牛仔外套", "category": "上装", "color": "#3b82f6"},
            {"id": 6, "name": "卡其色休闲裤", "category": "下装", "color": "#d4a574"},
        ]
