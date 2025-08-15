import os
import json
import requests
import time
import random
from typing import Dict, List
from dotenv import load_dotenv
from utils.custom_exception import RecommendationError
from utils.logger import logger

load_dotenv()

class AnimeRecommender:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama3-70b-8192")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.max_retries = 3
        self.base_delay = 1.5
        self.request_interval = 1.2
        self.timeout = 20

    def _validate_query(self, query: str) -> str:
        """Enhance queries lacking anime context"""
        query = query.strip().lower()
        anime_terms = {
            'action', 'comedy', 'romance', 'horror', 'sci-fi', 'fantasy',
            'drama', 'mecha', 'shounen', 'shoujo', 'seinen', 'josei',
            'slice of life', 'isekai', 'psychological', 'thriller', 'anime'
        }

        if not any(term in query for term in anime_terms):
            if len(query.split()) == 1:
                return f"anime about {query}"
            return f"anime that relates to {query}"
        return query

    def _build_payload(self, query: str) -> Dict:
        """Create optimized payload with relevance handling"""
        return {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": """You are an expert anime recommendation system.
                    For non-anime queries:
                    - Return anime with conceptual connections
                    - Score 60-80 with clear explanations
                    - Example: "apple" → "Fruit-themed anime"

                    For anime queries:
                    - Return direct matches
                    - Score 85-100
                    - Follow exact JSON format:
                    {
                        "recommendations": [
                            {
                                "title": "string",
                                "description": "string",
                                "score": int,
                                "genres": ["string"],
                                "year": int,
                                "why": "string"
                            }
                        ]
                    }"""
                },
                {
                    "role": "user",
                    "content": f"Recommend 5 anime for: '{query}'"
                }
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7,
            "max_tokens": 1200,
            "top_p": 0.9
        }

    def get_recommendations(self, query: str) -> List[Dict]:
        """Main recommendation method with enhanced query handling"""
        query = self._validate_query(query)
        payload = self._build_payload(query)
        last_request = 0

        for attempt in range(1, self.max_retries + 1):
            try:
                # Rate limiting
                elapsed = time.time() - last_request
                if elapsed < self.request_interval:
                    time.sleep(self.request_interval - elapsed)
                last_request = time.time()

                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout
                )

                if response.status_code >= 500:
                    raise requests.HTTPError(f"Server error {response.status_code}")

                response.raise_for_status()

                # Process response
                content = response.json()
                result = content['choices'][0]['message']['content']

                try:
                    data = json.loads(result)
                    if 'recommendations' not in data:
                        raise ValueError("Missing recommendations key")

                    # Validate recommendations
                    valid_recs = []
                    for rec in data['recommendations']:
                        if not all(k in rec for k in ['title', 'description', 'score']):
                            continue

                        valid_recs.append({
                            'anime': rec['title'],
                            'description': rec['description'],
                            'match_score': min(100, max(1, int(rec['score']))),
                            'genres': rec.get('genres', []),
                            'year': rec.get('year', ''),
                            'why': rec.get('why', '')
                        })

                    if not valid_recs:
                        raise ValueError("No valid recommendations")

                    logger.info(f"Processed {len(valid_recs)} recs for: '{query}'")
                    return valid_recs[:5]

                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Response validation failed: {str(e)}")
                    raise RecommendationError(
                        message="Invalid response format",
                        query=query,
                        model=self.model,
                        error_detail=e
                    )

            except requests.RequestException as e:
                delay = min(self.base_delay * (2 ** (attempt - 1)), 10) + random.random()
                logger.warning(f"Attempt {attempt} failed, retrying in {delay:.1f}s")
                time.sleep(delay)
                if attempt == self.max_retries:
                    raise RecommendationError(
                        message="Service unavailable after retries",
                        query=query,
                        model=self.model,
                        error_detail=e
                    )

        return []