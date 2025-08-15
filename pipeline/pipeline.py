from typing import List, Dict
from src.recommender import AnimeRecommender
from utils.custom_exception import RecommendationError
from utils.logger import logger

class AnimePipeline:
    def __init__(self):
        try:
            self.recommender = AnimeRecommender()
        except Exception as e:
            logger.error(f"Pipeline init failed: {str(e)}")
            raise RecommendationError(
                message="System initialization failed",
                error_detail=e
            )

    def recommend(self, query: str) -> List[Dict]:
        try:
            logger.info(f"Processing query: '{query}'")
            results = self.recommender.get_recommendations(query)

            if not results:
                logger.warning("No recommendations generated")
                return []

            logger.info(f"Generated {len(results)} recommendations")
            return results

        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            raise RecommendationError(
                message="Failed to generate recommendations",
                query=query,
                error_detail=e
            )