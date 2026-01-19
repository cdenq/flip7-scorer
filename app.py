import streamlit as st
from src.pages import scorer, advisor

PAGES = {
    "Scorer": scorer.show,
    "Advisor": advisor.show,
}


def main():
    st.set_page_config(page_title="Tofu's Flip Seven", layout="wide")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", list(PAGES.keys()))
    PAGES[page]()


if __name__ == "__main__":
    main()