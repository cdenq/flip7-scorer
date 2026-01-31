# ---------------------
# Imports
# ---------------------
import streamlit as st

# ---------------------
# Card Aliases (for easier typing on iPhone)
# ---------------------
CARD_ALIASES = {
    "-2": "+2",
    "-4": "+4",
    "-6": "+6",
    "-8": "+8",
    "-10": "+10",
    "!": "x2",
    "$": "sc",
    "&": "fr",
    "@": "f3",
}


def normalize_card(card):
    return CARD_ALIASES.get(card, card)


# ---------------------
# Legend Render Functions
# ---------------------
def render_card_types():
    st.markdown("`0`-`12`, `+2`, `+4`, `+6`, `+8`, `+10`, `x2`, `sc`, `f3`, `fr` | `sc` = second chance, `f3` = flip 3, `fr` = freeze")

def render_aliases():
    st.markdown("`+{n}`=`-{n}` | `x2`=`!` | `sc`=`$` | `fr`=`&` | `f3`=`@`")

def render_legend():
    render_card_types()
    render_aliases()
