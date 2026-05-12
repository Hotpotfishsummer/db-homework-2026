import random


class AIService:
    """
    Handles AI-driven features:
      - daily outfit recommendations
      - weather-aware styling tips
      - (future) LLM-based natural language wardrobe queries
    """

    def __init__(self):
        self._demo_tips = [
            "Layer a light cardigan over a cotton tee for variable spring weather.",
            "Earth tones pair well with navy — try beige chinos today.",
            "A structured blazer elevates even the simplest monochrome outfit.",
            "When in doubt, match your belt to your shoes for cohesion.",
        ]

    async def get_daily_tips(self, user_id: str | None = None) -> dict:
        """
        Stub implementation:
          - Returns a random demo tip.

        TODO:
          1. Call weather API using user's location.
          2. Query user's wardrobe DB for available garments.
          3. Prompt LLM with weather + wardrobe context.
        """
        tip = random.choice(self._demo_tips)
        return {
            "tip": tip,
            "weather_summary": None,
            "wardrobe_items_considered": 0,
            "generated_by": "stub",
        }
