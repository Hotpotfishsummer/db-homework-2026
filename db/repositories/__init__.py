from db.repositories.user_repo import UserRepository, UserProfileRepository
from db.repositories.wardrobe_repo import ClothesRepository, WardrobeRepository
from db.repositories.recommendation_repo import RecommendationRepository
from db.repositories.activity_repo import FavoriteRepository, HistoryRepository
from db.repositories.daily_tip_repo import DailyTipRepository
from db.repositories.shopping_recommendation_repo import ShoppingRecommendationRepository

__all__ = [
    "UserRepository", "UserProfileRepository",
    "ClothesRepository", "WardrobeRepository",
    "RecommendationRepository", "FavoriteRepository", "HistoryRepository",
    "DailyTipRepository", "ShoppingRecommendationRepository",
]
