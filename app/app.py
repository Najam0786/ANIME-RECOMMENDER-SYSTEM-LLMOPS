import streamlit as st
from pipeline.pipeline import AnimePipeline
from dotenv import load_dotenv
import time
from typing import Dict
from utils.logger import logger

load_dotenv()

def display_recommendation(anime: Dict, idx: int):
    """Display recommendation card with relevance indicators"""
    with st.container(border=True):
        cols = st.columns([1, 4, 1])
        with cols[0]:
            st.markdown(f"### #{idx + 1}")
        with cols[1]:
            st.subheader(anime['anime'])

            # Metadata row
            meta_cols = st.columns(3)
            with meta_cols[0]:
                if anime.get('year'):
                    st.caption(f"📅 {anime['year']}")
            with meta_cols[1]:
                if anime.get('genres'):
                    st.caption(f"🏷️ {', '.join(anime['genres'])}")
            with meta_cols[2]:
                score = anime['match_score']
                st.caption(f"⭐ {score}/100")

            # Relevance warning
            if score < 75:
                st.warning("Conceptual match - not directly related")

            st.write(anime['description'])

            # Explanation expander
            with st.expander("🔍 Why recommended?"):
                st.write(anime.get('why', 'Matches your search criteria'))
        with cols[2]:
            st.progress(anime['match_score'] / 100)

def main():
    st.set_page_config(
        page_title="AnimeFinder Pro",
        page_icon="🍿",
        layout="wide"
    )

    # Custom CSS
    st.markdown("""
    <style>
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
    }
    .stProgress > div > div > div {
        background-color: #FF4B4B;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🍿 AnimeFinder Pro")
    st.caption("Discover anime for any interest")
    st.markdown("---")

    # Session state
    if 'last_results' not in st.session_state:
        st.session_state.last_results = []
        st.session_state.last_query = ""

    # Search form
    with st.form("search_form"):
        query = st.text_input(
            "What are you interested in?",
            placeholder="e.g. 'action' or 'apple'",
            help="Try any topic - we'll find relevant anime!"
        )

        submitted = st.form_submit_button("Find Recommendations")

    # Handle search
    if submitted:
        if not query or len(query.strip()) < 2:
            st.warning("Please enter at least 2 characters")
        else:
            with st.spinner("Finding the perfect matches..."):
                start_time = time.time()
                try:
                    pipeline = AnimePipeline()
                    recommendations = pipeline.recommend(query.strip())
                    st.session_state.last_results = recommendations
                    st.session_state.last_query = query

                    if recommendations:
                        st.success(f"Found {len(recommendations)} recommendations")
                        st.caption(f"Generated in {time.time()-start_time:.1f}s")

                        for i, anime in enumerate(recommendations):
                            display_recommendation(anime, i)
                    else:
                        st.warning("No matches found. Try different keywords.")

                except Exception as e:
                    st.error("Service temporarily unavailable")
                    with st.expander("Details"):
                        st.write("""
                        **Try these solutions:**
                        - Check your internet connection
                        - Try again in a minute
                        - Use more specific terms
                        """)
                        st.code(str(e))

    # Show history
    if st.session_state.last_results:
        st.markdown("---")
        st.caption(f"Last search: '{st.session_state.last_query}'")
        if st.button("Search Again"):
            st.rerun()

if __name__ == "__main__":
    main()