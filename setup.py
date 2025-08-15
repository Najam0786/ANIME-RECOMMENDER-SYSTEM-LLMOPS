from setuptools import setup, find_packages

# Read dependencies from requirements.txt
with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="new_anime_recommender",
    version="0.1.0",
    author="Nazmul Mustufa Farooquee",
    description="Anime Recommender System using LangChain, HuggingFace, Groq, and ChromaDB",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    python_requires=">=3.9"
)
