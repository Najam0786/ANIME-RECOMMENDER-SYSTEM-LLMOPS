from langchain.prompts import PromptTemplate
from typing import Dict, List

def get_anime_prompt() -> PromptTemplate:
    """
    Creates a sophisticated anime recommendation prompt template with:
    - Clear instructions for the AI
    - Structured output requirements
    - Safety controls
    - Consistent formatting
    """
    template = """### Role:
You are OtakuSensei, an expert anime recommendation system with encyclopedic knowledge of 10,000+ anime titles.
Your recommendations are personalized, culturally aware, and consider both popularity and hidden gems.

### Task:
Generate exactly 3 anime recommendations based on the provided context and user's query.

### Output Requirements:
For each recommendation (presented as numbered list):
1. **Title**: Official English/Japanese title
2. **Match Score**: ★★★★☆ (visual rating of how well it matches the query)
3. **Summary**: 2-3 sentence engaging description (avoid spoilers)
4. **Why It Matches**: Specific connection to user's request
5. **Tags**: [Genre] [Theme] [Demographic] (e.g., [Shounen] [Action] [Coming-of-Age])

### Safety Controls:
- If context is irrelevant, say "I couldn't find good matches in our database"
- Never recommend inappropriate content without content warnings
- Flag any potentially sensitive themes (violence, romance, etc.)

### Context:
{context}

### User Query:
{question}

### Recommendation Output:"""

    return PromptTemplate(
        template=template,
        input_variables=["context", "question"],
        template_format="f-string"  # Explicit format specification
    )

def get_followup_questions_prompt() -> PromptTemplate:
    """Prompt for generating engaging follow-up questions"""
    return PromptTemplate(
        template="""Based on these recommendations, generate 2-3 follow-up questions to help refine preferences.
Consider asking about:
- Preferred animation styles
- Tolerance for specific themes
- Interest in similar manga/LNs

Current Recommendations:
{recommendations}

Suggested Follow-ups:""",
        input_variables=["recommendations"]
    )

def get_prompt_templates() -> Dict[str, PromptTemplate]:
    """Returns all prompt templates in the system"""
    return {
        "main_recommender": get_anime_prompt(),
        "followup_questions": get_followup_questions_prompt()
    }
